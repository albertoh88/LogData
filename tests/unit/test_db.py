import unittest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from db_nosql import Nosql

class TestNosql(unittest.TestCase):

    def setUp(self):
        patcher_config = patch('services.config')
        patcher_conn = patch('conection.Connection.connection_nosql')

        self.addCleanup(patcher_config.stop)
        self.addCleanup(patcher_conn.stop)

        self.mock_config = patcher_config.start()
        self.mock_connection_nosql = patcher_conn.start()

        self.mock_config.side_effect = lambda key: {'BD': 'test_db', 'COLLECTION_COMPANIES': 'companies'}[key]

        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()

        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.return_value = self.mock_collection
        self.mock_connection_nosql.return_value = self.mock_client

        self.nosql = Nosql()

    def test_verify_company_returns_public_key(self):

        self.mock_collection.find_one.return_value = {
            'company_name': 'MyCompany',
            'company_public_key': 'ABC123'
        }

        result = self.nosql.verify_company('MyCompany')
        self.assertEqual(result, 'ABC123')

        self.mock_collection.find_one.assert_called_once_with({'company_name': 'MyCompany'})

    def test_verify_company_not_found_raises_exception(self):

        self.mock_collection.find_one.return_value = None

        with self.assertRaises(HTTPException) as cm:
            self.nosql.verify_company('UnknownCompany')

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn('Company does not exist.', str(cm.exception.detail))

    def test_verify_company_without_public_key_raises_exception(self):

        self.mock_collection.find_one.return_value = {'company_name': 'MyCompany'}

        with self.assertRaises(HTTPException) as cm:
            self.nosql.verify_company('MyCompany')

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn('Public key not found for the company.', str(cm.exception.detail))

    def test_store_company_in_db_existing_company_raises_exception(self):

        self.mock_collection.find_one.return_value = {'company_name': 'MyCompany'}

        with self.assertRaises(HTTPException) as cm:
            self.nosql.store_company_in_db('ABC123', 'ABC123', 'MyCompany', {'a@example.com'})

        self.assertEqual(cm.exception.status_code, 409)
        self.assertIn('Company already exists.', str(cm.exception.detail))

        self.mock_collection.insert_one.assert_not_called()

    def test_store_company_in_db_successfully_inserts_company(self):

        self.mock_collection.find_one.return_value = None

        result = self.nosql.store_company_in_db('ABC123', 'PUBKEY123', 'MyCompany', {'a@example.com'})

        self.mock_collection.insert_one.assert_called_once_with({
            'company_id': 'ABC123',
            'company_public_key': 'PUBKEY123',
            'company_name': 'MyCompany',
            'alert_emails': {'a@example.com'}})

        self.assertEqual(result, {'message': 'Company successfully registered.'})

    def test_get_company_exists(self):

        self.mock_collection.find_one.return_value = {'company_name': 'MyCompany'}

        result = self.nosql.get_company('MyCompany')

        self.assertEqual(result, {'company_name': 'MyCompany'})

    def test_get_company_not_found_raises_exception(self):

        self.mock_collection.find_one.return_value = None

        with self.assertRaises(HTTPException) as cm:
            self.nosql.get_company('MyCompany')

        self.assertEqual(cm.exception.status_code, 404)
        self.assertIn('Company not found.', str(cm.exception.detail))

