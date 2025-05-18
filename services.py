import jwt
import smtplib
import uuid
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from email.message import EmailMessage
from datetime import datetime, timedelta
from db_nosql import Nosql
from decouple import config
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

seguridad = HTTPBearer()

class Service:
    def __init__(self):
        self.nosql = Nosql()

    def generar_token_registro(self, email):
        exp = datetime.utcnow() + timedelta(minutes=15)
        payload = {
            'email': email,
            'purpose': 'register_company',
            'exp': exp
        }
        token = jwt.encode(payload, config('SECRET_KEY'), config('ALGORITHM'))
        return token

    def send_email_register(self, email, token: str):
        msg = EmailMessage()
        msg['Subject'] = 'Tu token de registro'
        msg['From'] = '<EMAIL>'
        msg['To'] = email
        msg.set_content(f'Token de verificación es:\n\n{token}\n\nVálido por 15 minutos.')

        with smtplib.SMTP('smtp.gmail.com', 465) as smtp:
            smtp.send_message(msg)

    def verify_token_register(self, token):
        try:
            payload = jwt.decode(token, config('SECRET_KEY'), config('ALGORITHM'))
            if payload.get('purpose') != 'register_company':
                raise HTTPException(status_code=401, detail='Token no válido para registro')
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    def verify_token_logs(self, credentials=Depends(seguridad)):
        token = credentials.credentials
        try:
            # Obtener el payload sin verificar la firma
            unverified_payload = jwt.decode(token, options={'verify_signature': False})
            iss = unverified_payload.get('iss')

            if not iss:
                raise HTTPException(status_code=401, detail='Invalid token: campo "iss" ausente.' )

            # Buscar clave pública de la empresa
            public_key = self.nosql.verify_company(iss)

        except Exception:
            raise HTTPException(status_code=401, detail="El token incorrecto.")

        try:
            # Verifica firma con la clave pública
            pyload = jwt.decode(token, public_key, algorithms='RS256')
            return pyload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Expired token")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def validar_clave_publica(self, pem_str: str):
        """ Validar que la clave pública tenga formato PEM correcto y sea un RSA válido."""
        if not pem_str.startswith('-----BEGIN CERTIFICATE-----') or not pem_str.endswith('-----END CERTIFICATE-----'):
            raise HTTPException(status_code=400, detail="Formato PEM incorrecto.")

        try:
            public_key = serialization.load_pem_public_key(
                pem_str.encode('utf-8'),
                backend=default_backend()
            )
            return public_key
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Clave pública inválida: {str(e)}")


    def register_company(self, data):
        # Validar formato y contenido de la clave
        self.validar_clave_publica(data['company_public_key'])
        company_id = str(uuid.uuid4())
        self.nosql.store_company_in_db(
            company_id=company_id,
            public_key=data['company_public_key'],
            company_name=data['company_name'],
            alert_emails=data['alert_emails']
        )
        return company_id

    def send_email_to_support_team(self, log_data, email):
        pass

    def send_critical_alert(self, log_data, company_name):
        obj = self.nosql.obtener_company(company_name)
        for email in obj['alert_emails']:
            self.send_email_to_support_team(log_data, email)

        pass

    def notify_on_slack(self, log_data):
        pass


    def process_log(self, log_data: dict, company_name: str):
        self.nosql.store_log_in_db(log_data, company_name)
        if log_data['level'] == 'ERROR':
            self.send_critical_alert(log_data, company_name)
            self.notify_on_slack(log_data)
            return {'message': 'Log guardado y mensaje enviado para soporte'}
        return {'message': 'Log guardado'}