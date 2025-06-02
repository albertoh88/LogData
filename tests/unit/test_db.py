import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from db_nosql import Nosql

class TestNosql(unittest.TestCase):

    def setUp(self):
        self.nosql = Nosql()

    @patch('conection.Connection.connection_nosql')
    @patch('services.config')
    def test_verify_company_returns_public_key(self, mock_config, mock_connection_nosql):
        mock_config.side_effect = lambda key: {'BD': 'test_db', 'COLLECTION_COMPANIES': 'companies'}[key]
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_connection_nosql.return_value = mock_client

        mock_collection.find_one.return_value = {
            'company_name': 'MyCompany',
            'company_public_key': 'ABC123'
        }

        result = self.nosql.verify_company('MyCompany')
        self.assertEqual(result, 'ABC123')

        mock_collection.find_one.assert_called_once_with({'company_name': 'MyCompany'})

    @patch('conection.Connection.connection_nosql')
    @patch('services.config')
    def test_verify_company_not_found_raises_exception(self, mock_config, mock_connection_nosql):
        mock_config.side_effect = lambda key: {'BD': 'test_db', 'COLLECTION_COMPANIES': 'companies'}[key]
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_connection_nosql.return_value = mock_client

        mock_collection.find_one.return_value = None

        with self.assertRaises(HTTPException) as cm:
            self.nosql.verify_company('UnknownCompany')

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn('Company does not exist.', str(cm.exception.detail))

    @patch('conection.Connection.connection_nosql')
    @patch('services.config')
    def test_verify_company_without_public_key_raises_exception(self, mock_config, mock_connection_nosql):
        mock_config.side_effect = lambda key: {'BD': 'test_db', 'COLLECTION_COMPANIES': 'companies'}[key]
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_connection_nosql.return_value = mock_client

        mock_collection.find_one.return_value = {'company_name': 'MyCompany'}

        with self.assertRaises(HTTPException) as cm:
            self.nosql.verify_company('MyCompany')

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn('Public key not found for the company.', str(cm.exception.detail))

    @patch('conection.Connection.connection_nosql')
    @patch('services.config')
    def test_store_company_in_db_existing_company_raises_exception(self, mock_config, mock_connection_nosql):
        mock_config.side_effect = lambda key: {'BD': 'test_db', 'COLLECTION_COMPANIES': 'companies'}[key]
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_connection_nosql.return_value = mock_client

        mock_collection.find_one.return_value = {'company_name': 'MyCompany'}

        with self.assertRaises(HTTPException) as cm:
            self.nosql.store_company_in_db('ABC123', 'ABC123', 'MyCompany', {'a@example.com'})

        self.assertEqual(cm.exception.status_code, 409)
        self.assertIn('Company already exists.', str(cm.exception.detail))

        mock_collection.insert_one.assert_not_called()

    @patch('conection.Connection.connection_nosql')
    @patch('services.config')
    def test_store_company_in_db_successfully_inserts_company(self, mock_config, mock_connection_nosql):
        mock_config.side_effect = lambda key: {'BD': 'test_db', 'COLLECTION_COMPANIES': 'companies'}[key]
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_connection_nosql.return_value = mock_client

        mock_collection.find_one.return_value = None

        result = self.nosql.store_company_in_db('ABC123', 'PUBKEY123', 'MyCompany', {'a@example.com'})

        mock_collection.insert_one.assert_called_once_with({
            'company_id': 'ABC123',
            'company_public_key': 'PUBKEY123',
            'company_name': 'MyCompany',
            'alert_emails': {'a@example.com'}})

        self.assertEqual(result, {'message': 'Company successfully registered.'})

