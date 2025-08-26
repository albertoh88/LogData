from decouple import config
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ConnectionFailure, ServerSelectionTimeoutError
import certifi

class Connection:
    def __init__(self):
        self.mongo_uri = (f"mongodb+srv://{config('NOSQL_USER')}:{config('NOSQL_PASSWORD')}"
                     f"@{config('NOSQL_HOST')}/{config('BD')}"
                     f"?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=false")

        self.client = None

    def connection_nosql(self):
        """
                Connects to MongoDB Atlas using the constructed URI.
                Returns a ready-to-use MongoClient object.
        """
        if self.client:
            return self.client

        try:
            self.client = MongoClient(self.mongo_uri,
                                      tls=True,
                                      tlsAllowInvalidCertificates=False,
                                      tlsCAFile=certifi.where(),
                                      serverSelectionTimeoutMS=20000)
            self.client.admin.command('ping')
            return self.client
        except (ConnectionFailure, ServerSelectionTimeoutError) as cf:
            print(f"Error de conexión: {cf}")
            raise cf
        except PyMongoError as err:
            print(f"Ocurrió un error con MongoDB: {err}")
            raise err

    def get_database(self):
        """
               Returns the database object configured in the .env.
        """

        if not self.client:
            self.connection_nosql()
        return self.client[config('BD')]