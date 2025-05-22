import unittest
import jwt
import datetime
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
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            cls.secret_key,
            cls.algorithm
        )

        cls.token_expirado = jwt.encode({
            'email': 'email@email.com',
            'purpose': 'register_company',
            'exp': datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        },
            cls.secret_key,
            cls.algorithm
        )

        cls.token_invalido = jwt.encode(
            {
                'email': 'email@email.com',
                'purpose': 'register',
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
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

    def test_token_valido(self):
        result = self.service.verify_registration_token(self.token_valido)
        self.assertIsInstance(result, dict)
        self.assertIn('email', result)
        self.assertEqual('register_company', result['purpose'])

    def test_token_expirado(self):
        with self.assertRaises(HTTPException) as cm:
            self.service.verify_registration_token(self.token_expirado)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(cm.exception.detail, 'Token has expired.')

    def test_token_invalid(self):
        with self.assertRaises(HTTPException) as cm:
            self.service.verify_registration_token(self.token_invalido)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(cm.exception.detail, 'Token is not valid for registration.')

    def test_token_mal_formado(self):
        with self.assertRaises(HTTPException) as cm:
            self.service.verify_registration_token(self.token_mal_formado)

        self.assertEqual(cm.exception.status_code, 401)
        self.assertEqual(cm.exception.detail, 'Invalid token.')

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
