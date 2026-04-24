import pytest

from app.services.transform_service import (
    MissingColumnsError,
    REQUIRED_COLUMNS,
    validate_and_load_dataframe,
)


def test_csv_valido_calcula_densidad_e_indice() -> None:
    raw = (
        "zona,poblacion,ingreso,educacion,negocios,superficie_km2\n"
        "Norte,1000,50000,12,30,10.0\n"
        "Sur,2000,80000,16,50,20.0\n"
    ).encode("utf-8")
    df = validate_and_load_dataframe(raw)
    assert len(df) == 2
    norte = df[df["zone_key"] == "norte"].iloc[0]
    assert norte["densidad_poblacional"] == pytest.approx(100.0)
    assert norte["indice_desarrollo"] >= 0.0


def test_sin_superficie_densidad_null() -> None:
    raw = (
        "zona,poblacion,ingreso,educacion,negocios\n"
        "Centro,500,40000,10,20\n"
    ).encode("utf-8")
    df = validate_and_load_dataframe(raw)
    assert pd_is_na(df.iloc[0]["densidad_poblacional"])


def pd_is_na(v: object) -> bool:
    import pandas as pd

    return bool(pd.isna(v))


def test_columnas_faltantes_error_claro() -> None:
    raw = "zona,poblacion\nA,1\n".encode("utf-8")
    with pytest.raises(MissingColumnsError) as exc:
        validate_and_load_dataframe(raw)
    assert exc.value.missing
    for req in ("ingreso", "educacion", "negocios"):
        assert req in exc.value.missing


def test_duplicado_misma_zona_ultima_gana() -> None:
    raw = (
        "zona,poblacion,ingreso,educacion,negocios\n"
        "X,1,1,1,1\n"
        "X,99,1,1,1\n"
    ).encode("utf-8")
    df = validate_and_load_dataframe(raw)
    assert len(df) == 1
    assert df.iloc[0]["poblacion"] == 99.0


def test_columnas_requeridas_documentadas() -> None:
    assert set(REQUIRED_COLUMNS) == {"zona", "poblacion", "ingreso", "educacion", "negocios"}
