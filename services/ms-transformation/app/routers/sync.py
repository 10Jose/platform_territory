"""
Endpoints de sincronización HU-07.

Flujo de ``POST /zones``:
1. Resolver el último dataset en ingesta (preferencia ``valid``, si no ``partial``).
2. Descargar CSV (solo lectura; no altera ingesta).
3. Validar columnas mínimas, normalizar con Pandas y transformar fila a fila.
4. Insertar ``TransformationRun`` y hacer upsert en ``TransformedZoneData`` por ``zone_code``.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.infrastructure.database import get_db
from app.domain.models import TransformationRun, TransformedZoneData
from app.services.ingestion_client import IngestionClient
import pandas as pd
import io
import logging
import unicodedata

logger = logging.getLogger(__name__)
router = APIRouter()

# Versión semántica de las reglas de negocio (auditoría en ``TransformationRun.rules_applied``).
RULES_VERSION = "1.0.0"
RULES_METADATA = {
    "version": RULES_VERSION,
    "applied_at_rule_set": "HU-07",
    "steps": [
        "fetch_latest_dataset_from_ingestion",
        "validate_required_columns",
        "pandas_normalization",
        "normalize_zone_names",
        "compute_density_and_indices",
        "dedupe_by_zone_code",
        "upsert_transformed_zone_data",
        "record_transformation_run",
    ],
}


def convert_education_to_years(value):
    """Convierte texto de escolaridad o número a años equivalentes; ``None`` si no es reconocible."""
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        pass
    text = str(value).lower().strip()
    mapping = {
        "ninguna": 0, "ninguno": 0,
        "primaria": 5, "primaria incompleta": 3,
        "secundaria": 11, "secundaria incompleta": 8,
        "bachiller": 11, "bachillerato": 11,
        "tecnica": 14, "tecnólogo": 14, "tecnologo": 14,
        "universitaria": 16, "profesional": 16,
        "postgrado": 18, "maestría": 18,
        "doctorado": 20,
    }
    return mapping.get(text, None)


def normalize_zone_name(name: str) -> str:
    """Mayúsculas, sin acentos y espacios colapsados (clave legible para comparar zonas)."""
    if not name or not isinstance(name, str):
        return ""
    name = name.upper()
    name = unicodedata.normalize("NFKD", name).encode("ASCII", "ignore").decode("ASCII")
    name = " ".join(name.split())
    return name


def zone_code_for_row(row) -> str:
    """Identificador estable: ``codigo``, ``zona_id`` o nombre normalizado (evita duplicados lógicos)."""
    raw_code = row.get("codigo")
    if raw_code is not None and not pd.isna(raw_code) and str(raw_code).strip() != "":
        return str(raw_code).strip()
    raw_id = row.get("zona_id")
    if raw_id is not None and not pd.isna(raw_id) and str(raw_id).strip() != "":
        return str(raw_id).strip()
    return normalize_zone_name(row["zona"]) or f"ROW_{row.name}"


def compute_density_and_indices(row, poblacion: float, ingreso: float, negocios: float):
    """
    Calcula densidad poblacional e índices 0..1.

    Si existe ``superficie_km2`` > 0, densidad = población / superficie.
    Columnas opcionales ``actividad_economica`` y ``presencia_comercial`` sustituyen heurísticas por ingreso/negocios.
    """
    sup = row.get("superficie_km2")
    if sup is not None and not pd.isna(sup):
        try:
            s = float(sup)
            if s > 0:
                population_density = int(round(poblacion / s))
            else:
                population_density = int(round((negocios * 10000.0) / max(poblacion, 1.0)))
        except (ValueError, TypeError):
            population_density = int(round((negocios * 10000.0) / max(poblacion, 1.0)))
    else:
        population_density = int(round((negocios * 10000.0) / max(poblacion, 1.0)))

    if "actividad_economica" in row.index and not pd.isna(row.get("actividad_economica")):
        try:
            economic_activity_index = float(min(1.0, max(0.0, float(row["actividad_economica"]))))
        except (ValueError, TypeError):
            economic_activity_index = float(min(1.0, max(0.0, ingreso / 100_000.0)))
    else:
        economic_activity_index = float(min(1.0, max(0.0, ingreso / 100_000.0)))

    if "presencia_comercial" in row.index and not pd.isna(row.get("presencia_comercial")):
        try:
            commercial_presence_index = float(min(1.0, max(0.0, float(row["presencia_comercial"]))))
        except (ValueError, TypeError):
            commercial_presence_index = float(
                min(1.0, max(0.0, (negocios * 1000.0) / max(poblacion, 1.0) / 50.0))
            )
    else:
        commercial_presence_index = float(
            min(1.0, max(0.0, (negocios * 1000.0) / max(poblacion, 1.0) / 50.0))
        )

    return population_density, economic_activity_index, commercial_presence_index


def transform_zone(row):
    """
    Convierte una fila del DataFrame en un dict listo para ORM.

    Returns
    -------
    dict | None
        ``None`` si la fila no cumple mínimos (educación o numéricos inválidos).
    """
    zone_name_raw = row["zona"]
    zone_name_normalized = normalize_zone_name(zone_name_raw)
    zone_code = zone_code_for_row(row)

    educacion_raw = row.get("educacion")
    educacion_years = convert_education_to_years(educacion_raw)
    if educacion_years is None:
        logger.warning("Educación no válida en fila, omitiendo: %s", row.to_dict())
        return None

    negocios_raw = row.get("negocios")
    if negocios_raw is None or pd.isna(negocios_raw) or str(negocios_raw).strip() == "":
        negocios = 0.0
    else:
        try:
            negocios = float(negocios_raw)
        except (ValueError, TypeError):
            negocios = 0.0

    try:
        poblacion = float(row["poblacion"])
        ingreso = float(row["ingreso"])
    except (ValueError, TypeError) as e:
        logger.warning("poblacion/ingreso inválidos: %s", e)
        return None

    population_density, economic_activity_index, commercial_presence_index = compute_density_and_indices(
        row, poblacion, ingreso, negocios
    )

    return {
        "zone_code": zone_code,
        "zone_name": zone_name_normalized,
        "population_density": population_density,
        "average_income": int(round(ingreso)),
        "education_level": int(round(educacion_years)),
        "economic_activity_index": economic_activity_index,
        "commercial_presence_index": commercial_presence_index,
        "other_variables_json": {
            "raw_poblacion": row["poblacion"],
            "raw_ingreso": row["ingreso"],
            "raw_educacion": educacion_raw,
            "raw_zone_name": zone_name_raw,
            "negocios": negocios,
            "density_formula": "poblacion/superficie_km2" if "superficie_km2" in row.index else "negocios_por_10k_hab",
        },
    }


@router.post("/zones")
async def sync_zones(db: AsyncSession = Depends(get_db)):
    """
    Ejecuta la transformación HU-07 sobre el último CSV disponible en ingesta.

    **Columnas obligatorias en el CSV:** ``zona``, ``poblacion``, ``ingreso``, ``educacion``.
    Opcionales usadas si existen: ``codigo``, ``zona_id``, ``negocios``, ``superficie_km2``,
    ``actividad_economica``, ``presencia_comercial``.

    Respuesta incluye ids de dataset de ingesta y de ``TransformationRun`` completado.
    """
    client = IngestionClient()

    try:
        datasets = await client.get_datasets(limit=1, validation_status="valid")
        if not datasets:
            datasets = await client.get_datasets(limit=1, validation_status="partial")
        if not datasets:
            raise HTTPException(404, "No hay datasets válidos o parcialmente válidos para sincronizar")
        latest = datasets[0]
        logger.info(
            "Dataset encontrado: ID=%s, archivo=%s, estado=%s",
            latest["id"],
            latest["file_name"],
            latest.get("validation_status"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error al obtener dataset: {str(e)}") from e

    try:
        file_content = await client.get_dataset_file(latest["id"])
        logger.info("Archivo descargado: %s bytes", len(file_content))
    except Exception as e:
        raise HTTPException(500, f"Error al descargar archivo: {str(e)}") from e

    try:
        df = pd.read_csv(io.BytesIO(file_content))
        df.columns = [str(c).strip().lstrip("\ufeff") for c in df.columns]
        df = df.sort_index().reset_index(drop=True)
        for col in df.select_dtypes(include=["float64", "float32"]).columns:
            df[col] = df[col].replace({pd.NA: None})
        logger.info("CSV leído: %s filas, columnas: %s", len(df), list(df.columns))
    except Exception as e:
        raise HTTPException(500, f"Error al leer CSV: {str(e)}") from e

    required = ["zona", "poblacion", "ingreso", "educacion"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise HTTPException(
            400,
            {"message": "El CSV no tiene las columnas obligatorias.", "columnas_faltantes": missing},
        )

    zones_by_code = {}
    for idx, row in df.iterrows():
        try:
            transformed = transform_zone(row)
            if transformed is not None:
                zones_by_code[transformed["zone_code"]] = transformed
            else:
                logger.info("Fila %s omitida por datos inválidos", idx)
        except Exception as e:
            logger.warning("Error en fila %s: %s", idx, e)

    zones_data = list(zones_by_code.values())

    if not zones_data:
        raise HTTPException(400, "No se pudo transformar ninguna fila")

    run = TransformationRun(
        dataset_load_id=latest["id"],
        status="running",
        rules_applied=RULES_METADATA,
        output_version=RULES_VERSION,
    )
    db.add(run)
    await db.flush()

    upserted = 0
    for zone in zones_data:
        stmt = insert(TransformedZoneData).values(
            transformation_run_id=run.id,
            zone_code=zone["zone_code"],
            zone_name=zone["zone_name"],
            population_density=zone["population_density"],
            average_income=zone["average_income"],
            education_level=zone["education_level"],
            economic_activity_index=zone["economic_activity_index"],
            commercial_presence_index=zone["commercial_presence_index"],
            other_variables_json=zone["other_variables_json"],
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_transformed_zone_zone_code",
            set_={
                "transformation_run_id": stmt.excluded.transformation_run_id,
                "zone_name": stmt.excluded.zone_name,
                "population_density": stmt.excluded.population_density,
                "average_income": stmt.excluded.average_income,
                "education_level": stmt.excluded.education_level,
                "economic_activity_index": stmt.excluded.economic_activity_index,
                "commercial_presence_index": stmt.excluded.commercial_presence_index,
                "other_variables_json": stmt.excluded.other_variables_json,
            },
        )
        await db.execute(stmt)
        upserted += 1

    run.status = "completed"
    run.finished_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(run)

    return {
        "message": "Sincronización completada",
        "dataset_id": latest["id"],
        "transformation_run_id": run.id,
        "zones_processed": len(zones_data),
        "upserted": upserted,
        "rules_version": RULES_VERSION,
        "dedupe_by_zone_code": True,
    }
