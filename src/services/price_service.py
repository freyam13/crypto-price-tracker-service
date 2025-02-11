import logging
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional

import requests
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from src.db.schema import metadata
from src.models.currency import PAIRS, CurrencyPair
from src.models.price import Price


class PriceService:
    def __init__(self, db_url: str, api_key: str):
        """
        Initialize price service.

        Arguments:
            db_url: database connection URL
            api_key: CoinGecko API key
        """
        # HACK: allow SQLite for testing, require PostgreSQL for production
        if not db_url or (
            not db_url.startswith("sqlite") and "postgresql" not in db_url
        ):
            raise ValueError("Invalid database URL")

        self.engine = create_engine(db_url)
        metadata.create_all(self.engine)
        self.base_url = "https://api.coingecko.com/api/v3/simple/price"
        self.logger = logging.getLogger(__name__)

    def fetch_prices(self) -> Dict[str, float]:
        """
        Fetch current prices for all configured pairs.

        Returns:
            dict mapping pair strings to current prices
        """
        current_prices = {}
        quote_groups: Dict[str, List[str]] = {}

        for pair in PAIRS:
            base, quote = pair.split("/")
            if quote not in quote_groups:
                quote_groups[quote] = []
            quote_groups[quote].append(base)

        try:
            for quote, bases in quote_groups.items():
                # convert symbols to CoinGecko IDs
                ids = [CurrencyPair.get_coingecko_id(base) for base in bases]

                params = {"ids": ",".join(ids), "vs_currencies": quote}

                response = requests.get(
                    self.base_url,
                    params=params,
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()

                data = response.json()

                for base in bases:
                    pair = f"{base}/{quote}"
                    current_prices[pair] = data[CurrencyPair.get_coingecko_id(base)][
                        quote
                    ]

        except Exception as e:
            self.logger.error(f"Error fetching prices: {str(e)}")
            raise

        return current_prices

    def store_prices(self, prices: Dict[str, float]) -> None:
        """
        Store prices in database.

        Arguments:
            prices: dict mapping pairs to prices
        """
        try:
            timestamp = datetime.now(UTC)
            self._last_update = timestamp

            with self.engine.connect() as conn:
                for pair, price in prices.items():
                    conn.execute(
                        text(
                            """
                            INSERT INTO price_history (pair, price, timestamp)
                            VALUES (:pair, :price, :timestamp)
                            """
                        ),
                        {"pair": pair, "price": price, "timestamp": timestamp},
                    )
                conn.commit()

        except SQLAlchemyError as e:
            self.logger.error(f"Database error: {str(e)}")
            raise

    @lru_cache(maxsize=32)
    def get_price_history(self, pair: str, hours: int = 24) -> List[Price]:
        """
        Get price history for a pair.

        Arguments:
            pair: trading pair string
            hours: number of hours of history to retrieve

        Returns:
            list of Price objects
        """
        self.get_price_history.cache_clear()

        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                        SELECT pair, price, timestamp
                        FROM price_history
                        WHERE pair = :pair
                        AND timestamp > :since
                        ORDER BY timestamp DESC
                        """
                    ),
                    {
                        "pair": pair,
                        "since": datetime.now(UTC) - timedelta(hours=hours),
                    },
                )

                return [
                    Price(pair=row.pair, price=row.price, timestamp=row.timestamp)
                    for row in result
                ]

        except SQLAlchemyError as e:
            self.logger.error(f"Database error: {str(e)}")
            raise

    @lru_cache(maxsize=32)
    def get_volatility_rank(self, pair: str) -> Optional[int]:
        """
        Calculate volatility rank for a pair.

        Arguments:
            pair: trading pair string

        Returns:
            rank (1-based) of pair's volatility among all pairs
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                        WITH pair_stddev AS (
                            SELECT
                                pair,
                                STDDEV(price) as std_dev
                            FROM price_history
                            WHERE timestamp >= NOW() - INTERVAL '24 HOURS'
                            GROUP BY pair
                            HAVING COUNT(*) > 1
                        ),
                        pair_ranks AS (
                            SELECT
                                pair,
                                RANK() OVER (ORDER BY std_dev DESC) as rank
                            FROM pair_stddev
                        )
                        SELECT rank
                        FROM pair_ranks
                        WHERE pair = :pair
                        """
                    ),
                    {"pair": pair},
                ).fetchone()

                return result[0] if result else None

        except SQLAlchemyError as e:
            self.logger.error(f"Database error: {str(e)}")
            raise
