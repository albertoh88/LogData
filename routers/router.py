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
    company_public_key: str  # PEM format as text
    alert_emails: list[EmailStr]  # List of valid emails

# Log structure schema
class EventShema(BaseModel):
    action: str
    category: str
    outcome: str
    reason: Optional[str]

class UserShema(BaseModel):
    id: str
    name: str
    ip: str
    agent: str

class LogSchema(BaseModel):
    timestamp: str
    host: str
    service: str
    level: str
    event: EventShema
    user: UserShema
    message: str
    tags: list

class LogItem(BaseModel):
    timestamp: Optional[str]
    host: Optional[str]
    service: Optional[str]
    level: Optional[str]
    event: Optional[EventShema]
    user: Optional[UserShema]
    message: Optional[str]
    tags: Optional[List[str]]

class LogResponse(BaseModel):
    logs: List[LogItem]

class LogSearchRequest(BaseModel):
    company_id: Optional[str]
    level: Optional[str]
    user: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    tags: Optional[List[str]]

# Endpoints
@router.post('/request_registration')
def request_registration(data: RegisterRequestSchema):
    token = service.generate_registration_token(data.email)
    service.send_registration_email(data.email, token)
    return {'message': 'A temporary registration email has been sent to your email.'}

@router.post("/register_company")
def register_company(data: CompanyRegisterSchema):
    try:
        service.verify_registration_token(data.token)
        company_id = service.register_company(data)
        return {'message': 'Company successfully registered', 'company_id': company_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logs")
def receive_logs(log: LogSchema, payload=Depends(service.verify_logs_token)):
    try:
        company_name = payload['iss']
        service.process_log(log.model_dump(), company_name)
        return {'message': 'Log successfully received', 'company': company_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/logs/search', response_model=LogResponse)
def search_logs(request: LogSearchRequest, payload=Depends(service.verify_logs_token)):
    try:
        filters = request.model_dump(exclude_none=True)
        logs = service.consult_filtered_logs(filters)
        return {'logs': logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error while searching logs: {str(e)}')
