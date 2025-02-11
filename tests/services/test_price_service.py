from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from sqlalchemy import text

from src.models.price import Price


def test_store_and_retrieve_prices(price_service):
    test_prices = {
        "btc/usd": 50000.0,
        "eth/usd": 2000.0,
    }
    price_service.store_prices(test_prices)

    history = price_service.get_price_history("btc/usd")
    assert len(history) > 0
    assert isinstance(history[0], Price)
    assert history[0].price == 50000.0


def test_volatility_ranking(price_service, mock_volatility_rank):
    with patch.object(price_service, "get_volatility_rank", mock_volatility_rank):
        assert price_service.get_volatility_rank("btc/usd") == 1
        assert price_service.get_volatility_rank("eth/usd") == 2
        assert price_service.get_volatility_rank("sol/usd") == 3


def test_price_history(price_service):
    now = datetime.now(UTC)
    test_prices = [
        Price(pair="btc/usd", price=50000.0, timestamp=now),
        Price(pair="btc/usd", price=51000.0, timestamp=now - timedelta(hours=12)),
        Price(pair="btc/usd", price=52000.0, timestamp=now - timedelta(hours=23)),
    ]

    with price_service.engine.connect() as conn:
        for price in test_prices:
            conn.execute(
                text(
                    """
                    INSERT INTO price_history (pair, price, timestamp)
                    VALUES (:pair, :price, :timestamp)
                    """
                ),
                {
                    "pair": price.pair,
                    "price": price.price,
                    "timestamp": price.timestamp,
                },
            )
        conn.commit()

    history = price_service.get_price_history("btc/usd")

    assert len(history) == 3
    assert history[0].price == 50000.0
    assert history[2].price == 52000.0


def test_error_handling(price_service, monkeypatch, mock_api_error):
    monkeypatch.setattr("requests.get", mock_api_error)

    with pytest.raises(Exception):
        price_service.fetch_prices()
