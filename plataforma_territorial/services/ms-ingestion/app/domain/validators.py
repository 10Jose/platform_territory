import pandas as pd

REQUIRED_COLUMNS = ['zona', 'poblacion', 'ingreso', 'educacion', 'negocios']
VALIDATION_RULES_VERSION = "1.0.0"


def convert_education_to_years(value):
    """Convertir texto a años."""
    if value is None or pd.isna(value)):
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


def validate_dataset(df: pd.DataFrame):

    # Verificar columnas requeridas
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Columnas faltantes: {missing}")

    df_valid = df.copy()

    # Convertir columnas numericas
    numeric_cols = ['poblacion', 'ingreso', 'negocios']
    for col in numeric_cols:
        df_valid[col] = pd.to_numeric(df_valid[col], errors='coerce')

    # Convertir educación de texto a anos
    df_valid['educacion'] = df_valid['educacion'].apply(convert_education_to_years)

    errors = []

    for idx, row in df_valid.iterrows():
        row_errors = []

        # Validar zona
        if pd.isna(row['zona']) or str(row['zona']).strip() == '':
            row_errors.append("zona vacía o nula")

        # Validar poblacion, ingreso, negocios
        for col in numeric_cols:
            val = row[col]
            original_val = df.loc[idx, col]

            if pd.isna(val):
                if not pd.isna(original_val) and str(original_val).strip() != '':
                    row_errors.append(f"{col} debe ser un número válido (valor: '{original_val}')")
                else:
                    row_errors.append(f"{col} nulo o vacío")
            elif val <= 0:
                row_errors.append(f"{col} debe ser positivo (valor: {val})")

        # Validar educacion
        educ_val = row['educacion']
        original_educ = df.loc[idx, 'educacion']

        if pd.isna(educ_val):
            if not pd.isna(original_educ) and str(original_educ).strip() != '':
                row_errors.append(f"educacion no se pudo convertir a años (valor: '{original_educ}')")
            else:
                row_errors.append("educacion nulo o vacío")
        elif educ_val < 0:
            row_errors.append(f"educacion debe ser positivo (valor: {educ_val})")

        if row_errors:
            errors.append({
                "row": int(idx),
                "row_data": df.loc[idx].to_dict(),
                "errors": row_errors
            })

    valid_count = len(df) - len(errors)
    invalid_count = len(errors)

    return valid_count, invalid_count, errors, VALIDATION_RULES_VERSION