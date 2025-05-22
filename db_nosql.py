from decouple import config
from fastapi import HTTPException
from datetime import datetime
from conection import Connection


class Nosql:
    def __init__(self):
        self.conn = Connection()

    def verify_company(self, company_name):
        try:
            cliente = self.conn.connection_nosql()
            db = cliente[config('BD')]
            collection = db[config('COLLECTION_COMPANIES')]

            company = collection.find_one({'company_name': company_name})

            if not company:
                raise HTTPException(status_code=404, detail='Company does not exist.')

            public_key = company.get('company_public_key')
            if not public_key:
                raise HTTPException(status_code=404, detail='Public key not found for the company.')

            return public_key
        except Exception:
            raise

    def store_company_in_db(self, company_id, public_key, company_name, alert_emails):
        try:
            cliente = self.conn.connection_nosql()
            db = cliente[config('BD')]
            collection = db[config('COLLECTION_COMPANIES')]

            existing = collection.find_one({'company_name': company_name})
            if existing:
                raise HTTPException(status_code=409, detail='Company already exists.')

            collection.insert_one({'company_id': company_id,
                                   'company_public_key': public_key,
                                   'company_name': company_name,
                                   'alert_emails': alert_emails})

            return {'message': 'Company successfully registered.'}
        except Exception:
            raise

    def get_company(self, company_name):
        try:
            cliente = self.conn.connection_nosql()
            db = cliente[config('BD')]
            collection = db[config('COLLECTION_COMPANIES')]

            company = collection.find_one({'company_name': company_name})
            if not company:
                raise HTTPException(status_code=404, detail='Company not found.')

            return company
        except Exception:
            raise

    def store_log_in_db(self, log_data, company_name):
        try:
            client = self.conn.connection_nosql()
            db = client[config('BD')]
            collection = db[config('COLLECTION_LOGS')]

            company = self.get_company(company_name)

            # Ensure timestamp exists
            log_data['timestamp'] = log_data.get('timestamp', datetime.now())

            collection.insert_one({'company_id': company['company_id'],
                                   'company_name': company_name,
                                   'log': log_data,
                                   'received_at': datetime.now()})

        except Exception:
            raise

    def search_log_in_db(self, filters):
        try:
            client = self.conn.connection_nosql()
            db = client[config('BD')]
            collection = db[config('COLLECTION_LOGS')]
            result = list(collection.find(filters))
            return result
        except Exception:
            raise
