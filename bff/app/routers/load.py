<<<<<<< HEAD
=======
"""
Carga de archivos CSV hacia **ms-ingestion** (multipart).

Tras una carga exitosa dispara en segundo plano la sincronización HU-07 en **ms-transformation**.
"""
>>>>>>> origin/Miguel
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.ingestion_client import IngestionClient
from app.services.transformation_client import TransformationClient
from app.services.audit_client import AuditClient
from app.routers.auth import get_current_user
from app.domain.models import User
import logging
import asyncio

logger = logging.getLogger(__name__)

router = APIRouter()
audit_client = AuditClient()

async def sync_zones_background():
    """Sincroniza zonas en ms-transformation en segundo plano."""
    try:
        transformation_client = TransformationClient()
        result = await transformation_client.sync_zones()
        logger.info(f"Sincronización de zonas completada: {result}")
        await audit_client.log_event("SYNC_ZONES_SUCCESS", {"result": result})
    except Exception as e:
        logger.error(f"Error en sincronización de zonas: {e}")
        await audit_client.log_event("SYNC_ZONES_ERROR", {"error": str(e)})

@router.post("/")
async def upload_file(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user)
):
<<<<<<< HEAD
=======
    """Envía el CSV al servicio de ingesta y registra eventos de auditoría."""
>>>>>>> origin/Miguel
    logger.info(f"Endpoint /api/load llamado por usuario: {current_user.username}")
    try:
        client = IngestionClient()
        result = await client.upload(file, uploaded_by=current_user.username)

        # Auditoría de carga exitosa
        await audit_client.log_event("FILE_UPLOAD_SUCCESS", {
            "filename": file.filename,
            "user": current_user.username,
            "dataset_id": result.get("id"),
            "rows": result.get("rows"),
            "valid_rows": result.get("valid_rows"),
            "invalid_rows": result.get("invalid_rows")
        })

        # Sincronización en segundo plano
        asyncio.create_task(sync_zones_background())

        return result
    except HTTPException as e:
        logger.error(f"HTTPException: {e.status_code} - {e.detail}")
        await audit_client.log_event("FILE_UPLOAD_ERROR", {
            "filename": file.filename,
            "user": current_user.username,
            "error": e.detail,
            "status_code": e.status_code
        })
        raise
    except Exception as e:
        logger.exception("Error inesperado en upload_file")
        await audit_client.log_event("FILE_UPLOAD_ERROR", {
            "filename": file.filename,
            "user": current_user.username,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")