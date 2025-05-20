import jwt
import smtplib
import uuid
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone
from db_nosql import Nosql
from decouple import config
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

seguridad = HTTPBearer()

class Service:
    def __init__(self):
        self.nosql = Nosql()

    @staticmethod
    def generar_token_registro(email):
        exp = datetime.now(timezone.utc)  + timedelta(minutes=15)
        payload = {
            'email': email,
            'purpose': 'register_company',
            'exp': exp
        }
        token = jwt.encode(payload, config('SECRET_KEY'), config('ALGORITHM'))
        return token

    @staticmethod
    def send_email(subject, destinatario, contenido_text, remitente, psw, **options):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = remitente
        msg['To'] = destinatario

        if 'contenido_html' in options:
            msg.set_content(contenido_text)
            msg.add_alternative(options['registro'], subtype='html')
        else:
            msg.set_content(contenido_text)

        with smtplib.SMTP('smtp.gmail.com', 465) as smtp:
            smtp.login(remitente, psw)
            smtp.send_message(msg)

    def send_email_register(self, email, token: str):
        self.send_email(subject='Tu token de registro',
                        destinatario=email,
                        contenido_text=f'Token de verificación es:\n\n{token}\n\nVálido por 15 minutos.',
                        remitente=config('SENDER_MAIL'),
                        psw=config('PASSWORD'),)

    @staticmethod
    def verify_token_register(token):
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

    @staticmethod
    def validar_clave_publica(pem_str: str):
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

    def send_critical_alert(self, log_data, company_name):
        obj = self.nosql.obtener_company(company_name)
        for email in obj['alert_emails']:
            self.send_email(
                subject='Alerta Crítica - Error Grave Detectado.',
                destinatario=email,
                contenido_text=log_data,
                remitente=config('SENDER_MAIL'),
                psw=config('PASSWORD'),
            )

    def process_log(self, log_data: dict, company_name: str):
        self.nosql.store_log_in_db(log_data, company_name)
        if log_data['level'] == 'ERROR':
            self.send_critical_alert(log_data, company_name)
            return {'message': 'Log guardado y mensaje enviado para soporte'}
        return {'message': 'Log guardado'}

    def consultar_logs_con_filtros(self, data: dict):
        query = {}

        if 'empresa_id' in data:
            query['empresa_id'] = data['empresa_id']
        if 'nivel' in data:
            query['level'] = data['nivel']
        if 'usuario' in data:
            query['user.name'] = data['usuario']
        if 'tags' in data:
            query['tags'] = {'$in': data['tags']}
        if 'fecha_inicio' in data and 'fecha_fin' in data:
            query['timestamp'] = {
                '$gte': data['fecha_inicio'],
                '$lte': data['fecha_fin']
            }

        result = self.nosql.search_log_in_db(query)

        return result
    