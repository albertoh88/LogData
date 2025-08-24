# LogData

## 📦 Descrição

**LogData** é uma API desenvolvida em Python para gerenciar e registrar logs de sistemas de forma segura e organizada. Permite que empresas enviem logs, consultem dados históricos e apliquem filtros avançados, garantindo integridade e autenticidade das informações.

## 🚀 Funcionalidades principais

- ✅ API RESTful com endpoints claros e documentados. 
- ✅ Armazenamento de registros em banco de dados NoSQL.
- ✅ Assinatura e verificação com chaves públicas e privadas.

## 🛠️ Tecnologias utilizadas

![Python](https://img.shields.io/badge/Python-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg) ![Uvicorn](https://img.shields.io/badge/Uvicorn-ASGI%20Server-orange) ![MongoDB](https://img.shields.io/badge/MongoDB-NoSQL-green.svg) ![Criptografia](https://img.shields.io/badge/Criptografia-Hashing-lightgrey.svg) ![Unittest](https://img.shields.io/badge/Unittest-blueviolet.svg)

## ⚙️ Como instalar
Use o gerenciador de dependências pip para instalar os pacotes necessários.
**Clone o repositório**
```
git clone https://github.com/albertoh88/LogData.git
```
**Crie e ative um ambiente virtual**
**Windows**
```
python -m venv venv
venv\Scripts\activate
```
**Linux / MacOS**
```
python3 -m venv venv
source venv/bin/activate
```
**Instale as dependências**
```
pip install -r requirements.txt
```

Abra o arquivo **.env** e certifique-se de inserir seus dados de conexão com o banco de dados. Substitua host, porta, nome do banco, usuário e senha pelas suas credenciais do MongoDB. O código para criar o banco de dados MongoDB está no diretório principal.

Para executar a aplicação, use o arquivo **app.py**. A API estará disponível em **http://127.0.0.1:8000**

## 🔐 Autenticação e Tokens

Para verificar que os logs são enviados por entidades legítimas, cada requisição deve incluir um token JWT assinado com chave privada RSA. A chave pública da empresa deve estar registrada no servidor.

O token deve conter as seguintes informações:

```json
{
  "iss": "empresa_x",       // ✅ Obrigatório: identifica unicamente a empresa
  "sub": "log-agent",       // 🔍 Opcional: sistema ou módulo que gera o token
  "aud": "log-api",         // 🎯 Opcional: indica que o token é para sua API
  "iat": 1715778000,        // 🕒 Emitido em (timestamp UNIX)
  "exp": 1715781600,        // ⏳ Expira em (ex.: 1h depois)
  "scope": "log:write"      // 🔐 Opcional: níveis de acesso
}
```

## 📌 Como usar
Para enviar logs à API, você precisa de um token JWT válido incluído no header Authorization.

**Header de Autorização**
```bash
Authorization: Bearer <TOKEN_JWT>
```
**Endpoint principal**
```bash
POST /logs
```

**Exemplo de URL (local):**
```bash
http://localhost:8000/logs
```

**Corpo do request (JSON)**
```json
{
  "timestamp": "2025-05-21T14:32:00Z",
  "host": "server-01",
  "service": "auth",
  "level": "ERROR",
  "event": {
    "action": "login_attempt",
    "category": "authentication",
    "outcome": "failure",
    "reason": "invalid_password"
  },
  "user": {
    "id": "u1234",
    "name": "juan.perez",
    "ip": "192.168.1.23",
    "agent": "Mozilla/5.0"
  },
  "message": "Tentativa de login falhou para o usuário juan.perez",
  "tags": ["security", "login", "alerta"]
}
```
**Testando com Postman**

1. Abra o Postman e crie uma nova requisição POST.
2. Cole a URL do endpoint (http://localhost:8000/logs ou o link do Render).
3. No tab Headers, adicione:
   - Key: Authorization → Value: Bearer <TOKEN_JWT>
   - Key: Content-Type → Value: application/json
4. No tab Body, selecione raw e cole o JSON do log.
5. Clique em Send e veja a resposta da API.

**Testando com curl (opcional)**
```bash
curl -X POST http://localhost:8000/logs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN_JWT>" \
  -d '{
    "timestamp": "2025-05-21T14:32:00Z",
    "host": "server-01",
    "service": "auth",
    "level": "ERROR",
    "event": {
      "action": "login_attempt",
      "category": "authentication",
      "outcome": "failure",
      "reason": "invalid_password"
    },
    "user": {
      "id": "u1234",
      "name": "juan.perez",
      "ip": "192.168.1.23",
      "agent": "Mozilla/5.0"
    },
    "message": "Tentativa de login falhou para o usuário juan.perez",
    "tags": ["security", "login", "alerta"]
  }'
```
**Documentação automática**

O FastAPI gera automaticamente a documentação interativa da API.
Acesse em:
```bash
http://localhost:8000/docs
```
Permite testar todos os endpoints diretamente do navegador, sem precisar do Postman.

## 💬 Contato

[![GitHub](https://img.shields.io/badge/GitHub-albertoh88-black?logo=github)](https://github.com/albertoh88)

Notas adicionais Documentação OpenAPI: O FastAPI gera automaticamente uma interface interativa da API acessível em http://127.0.0.1:8000/docs. Não se esqueça se for usar o Uvicorn diretamente de rodar o servidor com :
```
uvicorn app:app --reload
```

## 📃 Licença
Este projeto está sob a - [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT). Consulte o arquivo para mais informações.