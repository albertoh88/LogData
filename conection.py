from decouple import config
from pymongo import MongoClient
from pymongo.errors import PyMongoError

class Connection:
    def __init__(self):
        pass

    @staticmethod
    def connection_nosql():
        try:
            cliente = MongoClient(host=config('NOSQL_HOST'),
                              port=int(config('NOSQL_PORT')))
            return cliente

        except PyMongoError as err:
            raise err
