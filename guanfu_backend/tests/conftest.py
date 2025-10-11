"""
Test configuration and fixtures for guanfu_backend tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """Create test database and tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with overridden database."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_place_data():
    """Sample place data for testing."""
    return {
        "name": "Test Emergency Shelter",
        "address": "123 Main St, Guangfu, Hualien",
        "address_description": "Near the community center",
        "coordinates": {
            "lat": 23.5678,
            "lng": 121.1234
        },
        "type": "shelter",
        "sub_type": "emergency",
        "info_sources": ["official", "verified"],
        "verified_at": 1728640000,
        "website_url": "https://example.com",
        "status": "open",
        "resources": [
            {"type": "bed", "quantity": 50},
            {"type": "blanket", "quantity": 100}
        ],
        "open_date": "2025-01-01",
        "end_date": "2025-12-31",
        "open_time": "00:00",
        "end_time": "23:59",
        "contact_name": "John Doe",
        "contact_phone": "+886-123-456789",
        "notes": "24/7 emergency shelter",
        "tags": [
            {"name": "emergency", "color": "red"},
            {"name": "verified", "color": "green"}
        ],
        "additional_info": {
            "capacity": 50,
            "accessible": True
        }
    }


@pytest.fixture
def sample_place_minimal_data():
    """Minimal required place data for testing."""
    return {
        "name": "Minimal Place",
        "address": "456 Test St",
        "coordinates": {
            "lat": 23.5,
            "lng": 121.1
        },
        "type": "resource_center",
        "status": "open",
        "contact_name": "Jane Smith",
        "contact_phone": "+886-987-654321"
    }
