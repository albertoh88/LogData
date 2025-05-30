import unittest
import jwt
import uuid
from datetime import datetime, timezone, timedelta
from services import Service
from fastapi import HTTPException
from unittest.mock import MagicMock, patch
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

class TestServices(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.service = Service()

        cls.secret_key = 'tu-clave-secreta-compartida'
        cls.algorithm = 'HS256'

        cls.token_valido = jwt.encode(
            {
                'email': 'email@email.com',
                'purpose': 'register_company',
                'exp': datetime.now(timezone.utc) + timedelta(hours=1)
            },
            cls.secret_key,
            cls.algorithm
        )

        cls.token_expirado = jwt.encode({
            'email': 'email@email.com',
            'purpose': 'register_company',
            'exp': datetime.now(timezone.utc) - timedelta(hours=1)
        },
            cls.secret_key,
            cls.algorithm
        )

        cls.token_invalido = jwt.encode(
            {
                'email': 'email@email.com',
                'purpose': 'register',
                'exp': datetime.now(timezone.utc) + timedelta(hours=1)
            },
            cls.secret_key,
            cls.algorithm
        )

        cls.token_mal_formado = 'esto-no-es-ub-token-jwt'

        cls.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        cls.private_pem = cls.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        cls.public_key = cls.private_key.public_key()
        cls.public_pem = cls.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        cls.invalid_public_key = """-----BEGIN PUBLIC KEY-----MIIBIjkkkkkkkkkBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsPWAZF
        8DEb4BqiQetahJ0ZsMHXwECbqYnhHaZ8/Z72kMwsQWos7z1X3vXzWV0yctIhRYua7Xdu9LOh7ZdPMrmhG8fsoB3T4J8jBfH0oEH7MyPcwKcSuXx
        XUaUya9ssXiqipnmzIeQn0c264EPXXjLVxKuNOsp8tWRkvDBAC5U+rUnr+Xr1XbsPbnqMm5xPDE3lQm9Evzh9HxZb3A9IFp30IJYTXfEt4tY9+2
        NLojmV6inxpaEE6utiuGQvwXHOUV9EnO4WiQQ1igFfvwsiJGwphxMUnQo8SDGFqZJWY0tGjflKpXlQcC5h2t9D/nEN6uWKg5jAAbitAahT8zaIu
        nNwIDAQAB-----END PUBLIC KEY-----\n"""

    @patch('services.jwt.encode')
    @patch('services.datetime')
    def test_generate_registration_token(self, mock_datetime, mock_jwt_encode):
        fixed_now = datetime(2025, 5, 27, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = fixed_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        mock_jwt_encode.return_value = 'token_mocker'

        token = self.service.generate_registration_token('test@example.com')

        expected_exp = fixed_now + timedelta(minutes=15)
        expected_payload = {
            'email': 'test@example.com',
            'purpose': 'register_company',
            'exp': expected_exp,
        }

        mock_jwt_encode.assert_called_once()
        called_args, called_kwargs = mock_jwt_encode.call_args
        payload_passed = called_args[0]

        assert payload_passed['email'] == expected_payload['email']
        assert payload_passed['purpose'] == expected_payload['purpose']
        assert payload_passed['exp'] == expected_payload['exp']

        self.assertEqual(token, 'token_mocker')

    @patch('services.smtplib.SMTP')
    def test_send_email(self, mock_smtp):
        subject = 'Teste Subject'
        addressee = 'receiver@example.com'
        content_text = 'Hello, this is a test.'
        sender = 'sender@example.com'
        psw = 'dummy_password'

        mock_smtp_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

        self.service.send_email(subject, addressee, content_text, sender, psw)

        mock_smtp.assert_called_with('smtp.gmail.com', 465)
        mock_smtp_instance.login.assert_called_once_with(sender, psw)
        mock_smtp_instance.send_message.assert_called_once()

        msg = mock_smtp_instance.send_message.call_args[0][0]
        self.assertEqual(msg['Subject'], subject)
        self.assertEqual(msg['To'], addressee)
        self.assertEqual(msg['From'], sender)

    @patch('services.config')
    @patch('services.Service.send_email')
    def test_send_registration_email_calls_send_email_correctly(self, mock_send_email, mock_config):
        mock_config.side_effect = lambda key: {
            'SENDER_MAIL': 'test@example.com',
            'PASSWORD': '1234'
        }[key]

        cls = self.__class__
        cls.service.send_registration_email('user@example.com', 'token123')

        mock_send_email.assert_called_once()
        args, kwargs = mock_send_email.call_args

        self.assertEqual(kwargs['subject'], 'Your registration token')
        self.assertEqual(kwargs['addressee'], 'user@example.com')
        self.assertIn('token123', kwargs['content_text'])
        self.assertIn('Valid for 15 minutes', kwargs['content_text'])
        self.assertEqual(kwargs['sender'], 'test@example.com')
        self.assertEqual(kwargs['psw'], '1234')

    def test_verify_registration_token_valido(self):
        result = self.service.verify_registration_token(self.token_valido)
        self.assertIsInstance(result, dict)
        self.assertIn('email', result)
        self.assertEqual('register_company', result['purpose'])

    def test_verify_registration_token_expirado(self):
        with self.assertRaises(HTTPException) as cm:
            self.service.verify_registration_token(self.token_expirado)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(cm.exception.detail, 'Token has expired.')

    def test_verify_registration_token_invalid(self):
        with self.assertRaises(HTTPException) as cm:
            self.service.verify_registration_token(self.token_invalido)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(cm.exception.detail, 'Token is not valid for registration.')

    def test_verify_registration_token_mal_formado(self):
        with self.assertRaises(HTTPException) as cm:
            self.service.verify_registration_token(self.token_mal_formado)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(cm.exception.detail, 'Invalid token.')

    @patch('services.jwt.decode')
    @patch('services.Nosql.verify_company')
    def test_verify_logs_token(self, mock_verify_company, mock_jwt_decode):
        mock_credentials = MagicMock()
        mock_credentials.credentials = 'fake.jwt.token'
        mock_jwt_decode.side_effect = [{'iss': 'empresa_alberto'}, {'sub': 'alberto'}]

        mock_verify_company.return_value = 'mi_clave_publica'

        result = self.service.verify_logs_token(mock_credentials)

        assert mock_jwt_decode.call_count == 2

        mock_jwt_decode.assert_any_call(
            mock_credentials.credentials,
            options={'verify_signature': False},
        )

        mock_verify_company.assert_called_once_with('empresa_alberto')

        mock_jwt_decode.assert_any_call(
            mock_credentials.credentials,
            'mi_clave_publica',
            algorithms='RS256',
        )

        self.assertEqual(result, {'sub': 'alberto'})

    @patch('services.jwt.decode')
    @patch('services.Nosql.verify_company')
    def test_verify_logs_token_raise_when_missing_iss_field(self, mock_verify_company, mock_jwt_decode):
        mock_credentials = MagicMock()
        mock_credentials.credentials = 'fake.jwt.token'
        mock_jwt_decode.side_effect = [{'sub': 'alberto'}, Exception('No se debería llamar')]

        with self.assertRaises(HTTPException) as cm:
            self.service.verify_logs_token(mock_credentials)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(cm.exception.detail, 'Invalid token: missing "iss" field.')

        mock_verify_company.assert_not_called()

    def test_validate_public_key(self):
        result = self.service.validate_public_key(self.public_pem)

        result_pem = result.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

        self.assertEqual(self.public_pem, result_pem)

    def test_invalid_format_pem(self):
        with self.assertRaises(HTTPException) as cm:
            self.service.validate_public_key('__Error__InvalidPublicKey__')

        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(cm.exception.detail, 'Invalid PEM format.')

    def test_invalid_public_key(self):
        with self.assertRaises(HTTPException) as cm:
            self.service.validate_public_key(self.invalid_public_key)

        self.assertEqual(cm.exception.status_code, 400)
        self.assertTrue(cm.exception.detail.startswith('Invalid public key'))

    @patch('services.Service.validate_public_key')
    @patch('services.uuid.uuid4')
    def test_register_company(self, mock_uuid, mock_validate):
        mock_uuid.return_value = uuid.UUID('12345678-1234-5678-1234-567812345678')
        mock_validate.return_value = None

        self.service.nosql = MagicMock()

        data = {
            'company_public_key': 'public_key_example',
            'company_name': 'MyCompany',
            'alert_emails': ['alert1@example.com', 'alert2@example.com']
        }
        result = self.service.register_company(data)

        mock_uuid.assert_called_once()

        self.service.nosql.store_company_in_db.assert_called_once_with(
            company_id='12345678-1234-5678-1234-567812345678',
            public_key='public_key_example',
            company_name='MyCompany',
            alert_emails=['alert1@example.com', 'alert2@example.com']
        )

        self.assertEqual(result, '12345678-1234-5678-1234-567812345678')

    @patch('services.Nosql')
    @patch('services.Service.send_email')
    def test_send_critical_alert_sends_emails_to_all_alert_recipients(self, mock_send_email, mock_nosql):
        mock_nosql_instance = mock_nosql.return_value
        mock_nosql_instance.get_company.return_value = {'alert_emails': ['a@example.com', 'b@example.com']}

        log_data = 'ERROR: Something critical happened!'
        company_name = 'MyCompany'

        service = Service()
        service.send_critical_alert(log_data, company_name)

        mock_nosql_instance.get_company.assert_called_once_with(company_name)
        calls = [
            unittest.mock.call(
                subject='Critical Alert - Severe Error Detected.',
                addressee='a@example.com',
                content_text=log_data,
                sender=unittest.mock.ANY,
                psw=unittest.mock.ANY,
            ),
            unittest.mock.call(
                subject='Critical Alert - Severe Error Detected.',
                addressee='b@example.com',
                content_text=log_data,
                sender=unittest.mock.ANY,
                psw=unittest.mock.ANY,
            ),
        ]
        mock_send_email.assert_has_calls(calls, any_order=True)

    @patch('services.Service.send_critical_alert')
    @patch('services.Nosql.store_log_in_db')
    def test_process_logs_error_level(self, mock_send_critical_alert, mock_store_log_in_db):
        log_data = {'timestamp': '2024-05-30T12:34:56Z',
                    'host': 'server-01',
                    'service': 'backend',
                    'level': 'ERROR',
                    'event': {'id': 1, 'description': 'Some event'},
                    'user': {'id': 1, 'name': 'Alberto'},
                    'message': 'Something critical happened!',
                    'tags': ['critical', 'urgent']}

        company_name = 'MyCompany'

        result = self.service.process_log(log_data, company_name)

        mock_store_log_in_db.assert_called_once_with(log_data, company_name)
        mock_send_critical_alert.assert_called_once_with(log_data, company_name)
        self.assertEqual(result, {'message': 'Log stored and support alert sent.'})

    @patch('services.Nosql.store_log_in_db')
    @patch('services.Service.send_critical_alert')
    def test_process_logs_non_error_level(self, mock_send_critical_alert, mock_store_log_in_db):
        log_data = {'timestamp': '2024-05-30T12:34:56Z',
                    'host': 'server-01',
                    'service': 'backend',
                    'level': 'INFO',
                    'event': {'id': 2, 'description': 'Some event'},
                    'user': {'id': 2, 'name': 'Alberto'},
                    'message': 'Something critical happened!',
                    'tags': ['critical', 'urgent']}

        company_name = 'MyCompany'

        result = self.service.process_log(log_data, company_name)

        mock_store_log_in_db.assert_called_once_with(log_data, company_name)
        mock_send_critical_alert.assert_not_called()
        self.assertEqual(result, {'message': 'Log stored successfully.'})

    @patch('services.Nosql.search_log_in_db')
    def test_consult_filtered_logs_builds_query_correctly(self, mock_search_log_in_db):
        data = {
            'company_id': '12345',
            'level': 'ERROR',
            'user': 'Alberto',
            'tags': ['critical', 'urgent'],
            'start_date': '2024-05-01T00:00:00Z',
            'end_date': '2024-05-30T23:59:59Z',
        }
        expected_query = {
            'company_id': '12345',
            'level': 'ERROR',
            'user.name': 'Alberto',
            'tags': {'$in': ['critical', 'urgent']},
            'timestamp': {
                '$gte': '2024-05-01T00:00:00Z',
                '$lte': '2024-05-30T23:59:59Z'
            }
        }

        mock_search_log_in_db.return_value = [{'log_id': 1}, {'log_id': 2}]

        result = self.service.consult_filtered_logs(data)

        mock_search_log_in_db.assert_called_once_with(expected_query)
        self.assertEqual(result, [{'log_id': 1}, {'log_id': 2}])
