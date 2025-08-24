from decouple import config
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ConnectionFailure

class Connection:
    def __init__(self):
        self.mongo_uri = (f"mongodb+srv://{config('NOSQL_USER')}:{config('NOSQL_PASSWORD')}"
                     f"@{config('NOSQL_HOST')}/{config('BD')}"
                     f"?retryWrites=true&w=majority&appName=Cluster0")

        self.client = None

    def connection_nosql(self):
        """
                Conecta-se ao MongoDB Atlas usando a URI construída.
                Retorna um objeto MongoClient pronto para uso.
        """
        try:
            self.client = MongoClient(self.mongo_uri)
            # Tentar uma operação rápida para validar a conexão
            self.client.admin.command('ping')
            return self.client
        except ConnectionFailure as cf:
            print(f"Error de conexión: {cf}")
            raise cf
        except PyMongoError as err:
            print(f"Ocurrió un error con MongoDB: {err}")
            raise err

    def get_database(self):
        """
               Retorna o objeto do banco de dados configurado no .env
        """

        if not self.client:
            self.connection_nosql()
        return self.client[config('BD')]