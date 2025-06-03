import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from routers.router import router

class TestRequestRegistrationEndpoint(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(router)

    @patch('services.Service.send_registration_email')
    @patch('services.Service.generate_registration_token')
    def test_request_registration_success(self, mock_generate_token, mock_send_email):
        mock_generate_token.return_value = 'dummy_token'
        email = 'test@example.com'

        response = self.client.post('/request_registration', json={'email': email})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'message': 'A temporary registration email has been sent to your email.'
        })

        mock_generate_token.assert_called_once_with(email)
        mock_send_email.assert_called_once_with(email, 'dummy_token')

    @patch('services.Service.register_company')
    @patch('services.Service.verify_registration_token')
    def test_register_company_success(self, mock_verify_token, mock_register_company):
        mock_register_company.return_value = 'company123'
        payload = {'token': 'valid_token', 'company_name': 'MyCompany', 'email': 'email@test.com',
                   'company_public_key': 'abc123xyz', 'alert_emails': ['alert1@test.com', 'alert2@test.com']}

        response = self.client.post('/register_company', json=payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'message': 'Company successfully registered.',
            'company_id': 'company123'
        })

        mock_verify_token.assert_called_once_with('valid_token')
        mock_register_company.assert_called_once()

    @patch('services.Service.register_company')
    @patch('services.Service.verify_registration_token')
    def test_register_company_invalid_token(self, mock_verify_token, mock_register_company):
        mock_verify_token.side_effect = HTTPException(status_code=401, detail='Invalid token')

        payload = {'token': 'bad_token', 'company_name': 'MyCompany', 'email': 'email@test.com',
                   'company_public_key': 'abc123xyz', 'alert_emails': ['alert1@test.com', 'alert2@test.com']}

        response = self.client.post('/register_company', json=payload)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {'detail': 'Invalid token'})

        mock_verify_token.assert_called_once_with('bad_token')
        mock_register_company.assert_not_called()

    @patch('services.Service.register_company')
    @patch('services.Service.verify_registration_token')
    def test_register_company_invalid_error(self, mock_verify_token, mock_register_company):
        mock_verify_token.return_value = None

        mock_register_company.side_effect = Exception('Unexpected error')

        payload = {'token': 'bad_token', 'company_name': 'MyCompany', 'email': 'email@test.com',
                   'company_public_key': 'abc123xyz', 'alert_emails': ['alert1@test.com', 'alert2@test.com']}

        response = self.client.post('/register_company', json=payload)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json(), {'detail': 'Unexpected error'})
