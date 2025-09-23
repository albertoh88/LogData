import jwt
import smtplib
import uuid
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from db_nosql import Nosql
from decouple import config
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

security = HTTPBearer()

class Service:
    def __init__(self):
        self.nosql = Nosql()

    @staticmethod
    def generate_registration_token(email):
        exp = datetime.now(timezone.utc)  + timedelta(minutes=15)
        payload = {
            'email': email,
            'purpose': 'register_company',
            'exp': exp
        }
        token = jwt.encode(payload, config('SECRET_KEY'), algorithm='HS256')
        return token

    @staticmethod
    def send_email(subject, addressee, content_text, sender='from@example.com'):
        sender_email = sender
        sender_user = config('MAILTRAP_USER')
        sender_password = config('MAILTRAP_PASSWORD')

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = addressee
        msg['Subject'] = subject

        msg.attach(MIMEText(content_text, 'plain'))

        with smtplib.SMTP('sandbox.smtp.mailtrap.io', 587) as server:
            server.starttls()
            server.login(sender_user, sender_password)

            server.sendmail(sender_email, addressee, msg.as_string())

        return {'success': True, 'message': f'O email foi enviado para {addressee}'}

    def send_registration_email(self, email, token: str):
        self.send_email(subject='Your registration token',
                        addressee=email,
                        content_text=f'Your verification token is:\n\n{token}\n\nValid for 15 minutes.')

    @staticmethod
    def verify_registration_token(token):
        try:
            payload = jwt.decode(token, config('SECRET_KEY'), config('ALGORITHM'))
            if payload.get('purpose') != 'register_company':
                raise HTTPException(status_code=401, detail='Token is not valid for registration.')
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token has expired.')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token.')

    def verify_logs_token(self, credentials=Depends(security)):
        token = credentials.credentials
        try:
            unverified_payload = jwt.decode(token, options={'verify_signature': False})

            if 'iss' not in unverified_payload:
                raise HTTPException(status_code=401, detail='Invalid token: missing "iss" field.' )

            iss = unverified_payload.get('iss')

            public_key = self.nosql.verify_company(iss)

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=401, detail='Invalid token.')

        try:
            pyload = jwt.decode(token, public_key, algorithms='RS256')
            return pyload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Token has expired.')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    @staticmethod
    def validate_public_key(pem_str: str):
        """ Validate that the public key is a proper RSA PEM format."""
        pem_str = pem_str.strip()

        if not pem_str.startswith('-----BEGIN PUBLIC KEY-----') or not pem_str.endswith('-----END PUBLIC KEY-----'):
            raise HTTPException(status_code=400, detail='Invalid PEM format.')

        try:
            public_key = serialization.load_pem_public_key(
                pem_str.encode('utf-8'),
                backend=default_backend()
            )
            return public_key
        except Exception as e:
            raise HTTPException(status_code=400, detail=f'Invalid public key: {str(e)}')

    def register_company(self, data):
        self.validate_public_key(data.company_public_key)
        company_id = str(uuid.uuid4())
        self.nosql.store_company_in_db(
            company_id=company_id,
            public_key=data.company_public_key,
            company_name=data.company_name,
            alert_emails=data.alert_emails
        )
        return company_id

    def send_critical_alert(self, log_data, company_name):
        obj = self.nosql.get_company(company_name)
        for email in obj['alert_emails']:
            self.send_email(
                subject='Critical Alert - Severe Error Detected.',
                addressee=email,
                content_text=log_data
            )

    def process_log(self, log_data: dict, company_name: str):
        self.nosql.store_log_in_db(log_data, company_name)
        if log_data['level'] == 'ERROR':
            self.send_critical_alert(log_data, company_name)
            return {'message': 'Log stored and support alert sent.'}
        return {'message': 'Log stored successfully.'}

    def consult_filtered_logs(self, data: dict):
        query = {}

        if 'company_id' in data:
            query['company_id'] = data['company_id']
        if 'level' in data:
            query['level'] = data['level']
        if 'user' in data:
            query['user.name'] = data['user']
        if 'tags' in data:
            query['tags'] = {'$in': data['tags']}
        if 'start_date' in data and 'end_date' in data:
            query['log.timestamp'] = {
                '$gte': data['start_date'].isoformat() + "Z",
                '$lte': data['end_date'].isoformat() + "Z"
            }

        if not query:
            raise ValueError('No filters provided for log search')

        result = self.nosql.search_log_in_db(query)

        return result
    