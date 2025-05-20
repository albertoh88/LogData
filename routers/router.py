from services import Service
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException


router = APIRouter()
service = Service()


class RegisterRequestSchema(BaseModel):
    email: EmailStr

class CompanyRegisterSchema(BaseModel):
    token: str
    company_name: str
    company_public_key: str  # PEM como texto, no como `bytes`
    alert_emails: list[EmailStr]  # Lista de correos válidos

# Validar el cuerpo del log con Pydantic
class LogSchema(BaseModel):
    timestamp: str
    host: str
    service: str
    level: str
    event: dict
    user: dict
    message: str
    tags: list

class LogItem(BaseModel):
    timestamp: Optional[str]
    host: Optional[str]
    service: Optional[str]
    level: Optional[str]
    event: Optional[dict]
    user: Optional[dict]
    message: Optional[str]
    tags: Optional[List[str]]

class LogResponse(BaseModel):
    logs: List[LogItem]

class LogSearchRequest(BaseModel):
    empresa_id: Optional[str]
    nivel: Optional[str]
    usuario: Optional[str]
    fecha_inicio: Optional[datetime]
    fecha_fin: Optional[datetime]
    tags: Optional[List[str]]

@router.post('/solicitar_register')
def solicitar_register(data: RegisterRequestSchema):
    token = service.generar_token_registro(data.email)
    service.send_email_register(data.email, token)
    return {'message': 'Se ha enviado un token temporal a tu correo.'}

@router.post("/register_company")
def register_company(data: CompanyRegisterSchema):
    try:
        service.verify_token_register(data.token)
        company_id = service.register_company(data)
        return {'message': 'Empresa registrada con éxito', 'company_id': company_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logs")
def recibir_logs(log: LogSchema, payload=Depends(service.verify_token_logs)):
    try:
        company_name = payload['iss']
        service.process_log(log.model_dump(), company_name)
        return {'message': 'Log recibido con éxito', 'empresa': company_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/logs/search', response_model=LogResponse)
def search_logs(request: LogSearchRequest, payload=Depends(service.verify_token_logs)):
    try:
        filtros = request.model_dump(exclude_none=True)
        logs = service.consultar_logs_con_filtros(filtros)
        return {'logs': logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error buscando logs: {str(e)}')
