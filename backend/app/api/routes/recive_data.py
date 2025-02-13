from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config.logger_config import logger

router = APIRouter()

# Definir el modelo de datos esperado
class DataModel(BaseModel):
    data: str

# Endpoint GET normal
@router.post("/recive-data")
async def send_command(data: DataModel):
    if not data.data:
        raise HTTPException(status_code=400, detail="No se ha recibido ningún dato")

    # Aquí puedes procesar el comando (por ejemplo, guardarlo en la BD o enviarlo a otro servicio)
    logger.info(f"La data recibida es: {data.data}")

    return {"status": "Data recibida", "data": data.data}
