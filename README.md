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
```bash
git clone https://github.com/albertoh88/LogData.git
```
**Crie e ative um ambiente virtual**
**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```
**Linux / MacOS**
```bash
python3 -m venv venv
source venv/bin/activate
```
**Instale as dependências**
```bash
pip install -r requirements.txt
```
## ⚙️ Configuração do arquivo .env

Antes de rodar a API, crie seu próprio arquivo `.env` baseado no exemplo fornecido:

**Copiar exemplo para criar seu próprio .env**
```bash
cp .env.example .env
```

**Editar .env com credenciais válidas do MongoDB Atlas e dados de e-mail**
```bash
nano .env  # ou use seu editor preferido
```
**Certifique-se de preencher todas as variáveis corretamente, incluindo:**

 - NOSQL_HOST, NOSQL_PORT, NOSQL_USER, NOSQL_PASSWORD
 - BD, COLLECTION_LOGS, COLLECTION_COMPANIES
 - SECRET_KEY, PUBLIC_KEY, ALGORITHM
 - SENDER_MAIL, PASSWORD
 - PORT, HOST
 - 
Para executar a aplicação, use o arquivo **app.py**. A API estará disponível em **http://127.0.0.1:8000**

## 🔐 Autenticação e Tokens

Para verificar que os logs são enviados por entidades legítimas, cada requisição deve incluir um token JWT assinado com chave privada RSA. A chave pública da empresa deve estar registrada no servidor.

O token deve conter as seguintes informações:

```json
{
  "iss": "empresa_x",
  "sub": "log-agent",
  "aud": "log-api",
  "iat": 1715778000,
  "exp": 1715781600,
  "scope": "log:write"
}
```
## 📌 Descrição dos campos:

iss: Obrigatório, identifica unicamente a empresa
sub: Opcional, sistema ou módulo que gera o token
aud: Opcional, indica que o token é para sua API
iat: Emitido em (timestamp UNIX)
exp: Expira em (ex.: 1h depois)
scope: Opcional, níveis de acesso

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
## 🐳 Usando Docker

Se você quiser rodar a API diretamente usando a imagem do Docker Hub, siga estes passos:

Rodar a API com a imagem pronta
```bash
docker run -p 8000:8000 elflacorex/logdata:latest
```
A API estará acessível em: http://localhost:8000

Para quem quiser construir a imagem localmente
```bash
docker build -t logdata .
docker run -p 8000:8000 --env-file .env logdata:lastest
```
Testar a conexão de dentro do contêiner (opcional):
```bash
docker exec -it <container_id> bash
python -m tests.integration.test_connection
```
Subir a imagem para o Docker Hub (opcional)
```bash
docker login
docker tag logdata elflacorex/logdata:latest
docker push elflacorex/logdata:latest
```

Depois, qualquer usuário pode rodar:
```bash
docker run -p 8000:8000 elflacorex/logdata:latest
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
```bash
uvicorn app:app --reload
```

## 📃 Licença
Este projeto está sob a - [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT). Consulte o arquivo para mais informações.