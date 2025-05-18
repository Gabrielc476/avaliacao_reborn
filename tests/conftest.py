import os
import pytest
from typing import Generator, Dict, Any
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from utils.password import PasswordUtils
from utils.jwt import JWTUtils
from database.models.user import User
from database.connect import Base
from main import app
from dependencies import get_db

# Set up environment variables for testing
os.environ["JWT_SECRET_KEY"] = "test_secret_key"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["JWT_REFRESH_TOKEN_EXPIRE_DAYS"] = "7"

# In-memory SQLite database for testing
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine with SQLite
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Set up mocks for password and JWT utilities
@pytest.fixture(autouse=True)
def mock_password_utils():
    """Mock password utilities for all tests"""
    with patch.object(PasswordUtils, 'get_password_hash', return_value="hashed_password"):
        with patch.object(PasswordUtils, 'verify_password', return_value=True):
            yield


@pytest.fixture(autouse=True)
def mock_jwt_utils():
    """Mock JWT utilities for all tests"""
    with patch.object(JWTUtils, 'create_access_token', return_value="test_access_token"):
        with patch.object(JWTUtils, 'create_refresh_token', return_value="test_refresh_token"):
            with patch.object(JWTUtils, 'verify_token',
                              return_value=MagicMock(user_id=1, username="testuser", email="test@example.com")):
                yield


# Create all tables in the test database
@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Creates a fresh database for each test, then drops all tables after the test.
    Yields a SQLAlchemy Session that's bound to the test database.
    """
    # Import models here to ensure they're registered with the Base
    from database.models import User, Questionnaire, CustomTable, TableQuestionnaire, TableColumn, TableRow, CellValue, \
        QuestionnaireResponse

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create a new session for testing
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test finishes
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    Creates a FastAPI TestClient with the test database session.
    """

    # Override the get_db dependency to use the test database
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client

    # Reset the dependency override
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def test_user(test_db: Session) -> User:
    """
    Creates a test user in the database.
    """
    # Create test user
    test_user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )

    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)

    return test_user


@pytest.fixture(scope="function")
def test_user_token() -> Dict[str, Any]:
    """
    Creates test tokens for a user.
    """
    # Return mock tokens
    return {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "token_type": "bearer"
    }