from src.db.main import get_session
from unittest.mock import Mock
from src import app
import pytest
from fastapi.testclient import TestClient
from src.auth.dependencies import AcessTokenBearer, RoleChecker, RefreshTokenBearer


mock_session=Mock()
mock_user_service=Mock()
mock_book_service=Mock()


def get_mock_session():
    yield mock_session
    
access_token_bearer=AcessTokenBearer()
refresh_token_bearer=RefreshTokenBearer()
role_checker=RoleChecker()    

app.dependency_overrides[get_session]=get_mock_session
app.dependency_overrides[role_checker]=Mock()
app.dependency_overrides[refresh_token_bearer]=Mock()
@pytest.fixture
def fake_session():
    return mock_session

@pytest.fixture
def fake_user_service():
    return mock_user_service
@pytest.fixture
def test_client():
    return TestClient(app)