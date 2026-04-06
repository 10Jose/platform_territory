from __future__ import annotations

import io
import re
from typing import Any

import numpy as np
import pandas as pd

# Alineado con validación HU-02 / backlog
REQUIRED_COLUMNS = ("zona", "poblacion", "ingreso", "educacion", "negocios")
OPTIONAL_SUPERFICIE = ("superficie_km2", "superficie", "area_km2")


class MissingColumnsError(ValueError):
    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(
            "Faltan columnas obligatorias en el CSV. "
            f"Requeridas: {list(REQUIRED_COLUMNS)}. Faltantes: {missing}"
        )


def _norm_col(name: str) -> str:
    s = str(name).strip().lower()
    s = re.sub(r"\s+", "_", s)
    return s


def validate_and_load_dataframe(raw: bytes) -> pd.DataFrame:
    buffer = io.BytesIO(raw)
    try:
        df = pd.read_csv(buffer)
    except Exception as e:
        raise ValueError(f"No se pudo leer el CSV: {e}") from e

    df = df.rename(columns={c: _norm_col(c) for c in df.columns})

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise MissingColumnsError(missing)

    # Superficie opcional (primera columna reconocida)
    sup_col = next((c for c in OPTIONAL_SUPERFICIE if c in df.columns), None)

    # Tipos y nulos
    df["zona"] = df["zona"].astype(str).str.strip()
    for col in ("poblacion", "ingreso", "educacion", "negocios"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if sup_col:
        df["superficie_km2"] = pd.to_numeric(df[sup_col], errors="coerce")
    else:
        df["superficie_km2"] = np.nan

    # Normalización de nulos numéricos
    for col in ("poblacion", "ingreso", "educacion", "negocios"):
        df[col] = df[col].fillna(0.0)
    df["superficie_km2"] = pd.to_numeric(df["superficie_km2"], errors="coerce")

    df = df[df["zona"].str.len() > 0]
    df["zone_key"] = df["zona"].str.lower().str.strip()

    # Duplicados en el mismo archivo: última fila gana
    df = df.drop_duplicates(subset=["zone_key"], keep="last")

    # Reglas: densidad e índice
    df["densidad_poblacional"] = _densidad(df["poblacion"], df["superficie_km2"])
    df["indice_desarrollo"] = _indice_desarrollo(df)

    return df


def _densidad(poblacion: pd.Series, superficie: pd.Series) -> pd.Series:
    out = pd.Series(np.nan, index=poblacion.index, dtype="float64")
    mask = superficie.notna() & (superficie > 0)
    out.loc[mask] = (poblacion.loc[mask] / superficie.loc[mask]).astype(float)
    return out


def _indice_desarrollo(df: pd.DataFrame) -> pd.Series:
    """Índice 0–100 a partir de ingreso, educación y negocios normalizados en el lote."""
    cols = ["ingreso", "educacion", "negocios"]
    norms = []
    for c in cols:
        s = pd.to_numeric(df[c], errors="coerce").astype(float)
        r = float(s.max() - s.min())
        if r == 0 or pd.isna(r):
            norms.append(pd.Series(50.0, index=df.index))
        else:
            norms.append((s - s.min()) / r * 100.0)
    stacked = pd.concat(norms, axis=1)
    return stacked.mean(axis=1)


def build_rules_metadata(rules_version: str) -> dict[str, Any]:
    return {
        "version": rules_version,
        "required_columns": list(REQUIRED_COLUMNS),
        "optional_columns": list(OPTIONAL_SUPERFICIE),
        "densidad": "poblacion / superficie_km2 cuando superficie > 0; si no hay superficie, null",
        "indice_desarrollo": "media de ingreso, educacion y negocios normalizados 0–100 dentro del lote",
        "deduplicacion_csv": "última fila por zone_key",
    }
