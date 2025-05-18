# raiz/database/connect.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, registry, declarative_base
import os
from dotenv import load_dotenv


# Padrão Singleton para conexão com o banco de dados
class DatabaseConnection:
    _instance = None
    _engine = None
    _SessionLocal = None
    _Base = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._configure()
        return cls._instance

    @classmethod
    def _configure(cls):
        load_dotenv()

        # Configurações do PostgreSQL
        DB_USER = os.getenv("DB_USER", "postgres")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_NAME = os.getenv("DB_NAME", "questionnaires")

        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

        # Criar engine com PostgreSQL
        cls._engine = create_engine(DATABASE_URL)
        cls._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls._engine)

        # Usar registry para criar a base em estilo SQLAlchemy 2.0
        mapper_registry = registry()
        cls._Base = mapper_registry.generate_base()

    @property
    def engine(self):
        return self._engine

    @property
    def SessionLocal(self):
        return self._SessionLocal

    @property
    def Base(self):
        return self._Base

    def get_db(self):
        """Dependência para injeção da sessão do banco de dados no FastAPI"""
        db = self._SessionLocal()
        try:
            yield db
        finally:
            db.close()


# Exportar instância do singleton
db_connection = DatabaseConnection()
Base = db_connection.Base

# Para uso em outros módulos:
# from database.connect import db_connection, Base
#
# # Nas rotas FastAPI:
# @app.get("/rota")
# def rota(db: Session = Depends(db_connection.get_db)):
#     ...