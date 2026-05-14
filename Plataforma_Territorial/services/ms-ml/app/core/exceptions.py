from fastapi import HTTPException, status


class MLException(HTTPException):
    pass


class NoDataError(MLException):
    def __init__(self, detail: str = "No hay datos disponibles para entrenar el modelo"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class NoModelError(MLException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay un modelo entrenado. Entrena un modelo primero.",
        )


class TrainingError(MLException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en entrenamiento: {detail}",
        )


class UpstreamError(MLException):
    """Falla en la comunicación con un servicio dependiente (ms-analytics, ms-audit)."""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Servicio dependiente no disponible: {detail}",
        )
