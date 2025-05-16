import uvicorn
from routers import router
from fastapi import FastAPI

app = FastAPI()

# Definimos las rutas
app.include_router(router.router)

@app.get('/')
def read_root():
    return {"message": "Este es el primer endpoint"}

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
