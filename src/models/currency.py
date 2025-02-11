from enum import Enum
from typing import Final

from pydantic import BaseModel


class BaseCurrency(str, Enum):
    """
    Base currencies supported by the system.
    """

    BTC = "btc"
    ETH = "eth"
    SOL = "sol"
    ETC = "etc"
    DOT = "dot"
    ADA = "ada"
    BNT = "bnt"


class QuoteCurrency(str, Enum):
    """
    Quote currencies supported by the system.
    """

    USD = "usd"
    EUR = "eur"
    BTC = "btc"


class CoinGeckoId(str, Enum):
    """
    CoinGecko API identifiers for supported currencies.
    """

    ADA = "cardano"
    BNT = "bancor"
    BTC = "bitcoin"
    DOT = "polkadot"
    ETC = "ethereum-classic"
    ETH = "ethereum"
    SOL = "solana"


class CurrencyPair(BaseModel):
    """
    A trading pair combining base and quote currencies with CoinGecko ID lookup.
    """

    base: BaseCurrency
    quote: QuoteCurrency

    def __str__(self) -> str:
        return f"{self.base.value}/{self.quote.value}"

    @staticmethod
    def get_coingecko_id(currency: str) -> str:
        """
        Get CoinGecko API ID for a currency symbol.
        """
        try:
            return CoinGeckoId[currency.upper()].value

        except KeyError:
            raise ValueError(f"Unsupported currency: {currency}")


# supported trading pairs
PAIRS: Final = [
    str(CurrencyPair(base=BaseCurrency.BTC, quote=QuoteCurrency.USD)),
    str(CurrencyPair(base=BaseCurrency.ETH, quote=QuoteCurrency.USD)),
    str(CurrencyPair(base=BaseCurrency.SOL, quote=QuoteCurrency.USD)),
    str(CurrencyPair(base=BaseCurrency.ETC, quote=QuoteCurrency.EUR)),
    str(CurrencyPair(base=BaseCurrency.DOT, quote=QuoteCurrency.USD)),
    str(CurrencyPair(base=BaseCurrency.ADA, quote=QuoteCurrency.USD)),
    str(CurrencyPair(base=BaseCurrency.ETH, quote=QuoteCurrency.BTC)),
    str(CurrencyPair(base=BaseCurrency.BNT, quote=QuoteCurrency.BTC)),
]
