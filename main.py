# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from routes import api_router

# Carregar variáveis de ambiente
load_dotenv()

# Obter configurações do ambiente
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
APP_NAME = os.getenv("APP_NAME", "Plataforma de Questionários Psicológicos")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"

# Configuração da aplicação FastAPI
app = FastAPI(
    title=APP_NAME,
    description="API para gerenciamento e análise de questionários psicológicos",
    version="1.0.0",
    debug=DEBUG
)

# Adicionar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir todas as rotas da API
app.include_router(api_router, prefix="/api")

# Rota raiz
@app.get("/")
async def root():
    return {
        "message": "Bem-vindo à API de Questionários Psicológicos",
        "docs": "/docs",
        "version": "1.0.0"
    }

# Verificação de saúde da aplicação
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)