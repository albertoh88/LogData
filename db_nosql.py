from decouple import config
from fastapi import HTTPException
from datetime import datetime
from conection import Connection


class Nosql:
    def __init__(self):
        self.conn = Connection()

    def verify_company(self, iss):
        try:
            cliente = self.conn.connection_nosql()
            db = cliente[config('BD')]
            collection = db[config('COLLECTION_COMPANIES')]

            # Verificar si el nombre de la compañía está registrado.
            obj = collection.find_one({'company_name': iss})

            if not obj:
                raise HTTPException(status_code=404, detail='Company inexistent')

            company_public_key = obj.get('public_key')
            if not company_public_key:
                raise HTTPException(status_code=404, detail='Clave publica no encontrada para la empresa')

            return company_public_key
        except Exception as e:
            raise e

    def store_company_in_db(self, company_id, public_key, company_name, alert_emails):
        try:
            cliente = self.conn.connection_nosql()
            db = cliente[config('BD')]
            collection = db[config('COLLECTION_COMPANIES')]

            obj = collection.find_one({'company_name': company_name})
            if not obj:
                raise HTTPException(status_code=404, detail='Company existent')

            collection.insert_one({'company_id': company_id,
                                   'company_public_key': public_key,
                                   'company_name': company_name,
                                   'alert_emails': alert_emails})

            return {'message': 'Company successfully registered'}
        except Exception as e:
            raise e

    def obtener_company(self, company_name):
        try:
            cliente = self.conn.connection_nosql()
            db = cliente[config('BD')]
            collection = db[config('COLLECTION_COMPANIES')]
            obj = collection.find_one({'company_name': company_name})
            if not obj:
                raise HTTPException(status_code=404, detail='Company does not exist')
            return obj
        except Exception as e:
            raise e

    def store_log_in_db(self, log_data, company_name):
        try:
            client = self.conn.connection_nosql()
            db = client[config('BD')]
            collection = db[config('COLLECTION_LOGS')]

            company = self.obtener_company(company_name)

            collection.insert_one({'company_id': company['company_id'],
                                   'company_name': company_name,
                                   'log': log_data,
                                   'received_at': datetime.now()})
        except Exception as e:
            raise e