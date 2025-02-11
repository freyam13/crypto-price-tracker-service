import pytest
from sqlalchemy import create_engine

from src.db.schema import metadata
from src.services.price_service import PriceService


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def price_service(test_db):
    return PriceService(db_url="sqlite:///:memory:", api_key="test-api-key")


@pytest.fixture
def mock_volatility_rankings():
    return {
        "btc/usd": 1,
        "eth/usd": 2,
        "sol/usd": 3,
    }


@pytest.fixture
def mock_volatility_rank(mock_volatility_rankings):

    def _mock_rank(pair: str) -> int:
        return mock_volatility_rankings.get(pair, 0)

    return _mock_rank


@pytest.fixture
def mock_api_error():

    def mock_get(*args, **kwargs):
        raise Exception("API Error")

    return mock_get
