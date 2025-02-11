from fastapi import FastAPI, HTTPException

from config import COINGECKO_API_KEY, DB_URL
from src.models.currency import PAIRS
from src.models.price import Price, PriceHistory
from src.services.price_service import PriceService

app = FastAPI(title="Crypto Price API")
service = PriceService(
    db_url=DB_URL,
    api_key=COINGECKO_API_KEY,
)


@app.get("/api/prices/{base_currency}/{quote_currency}/current")
async def get_current_price(base_currency: str, quote_currency: str) -> Price:
    """
    Get current price for a trading pair.

    Arguments:
        base_currency: the currency being priced (e.g. 'btc')
        quote_currency: the currency used for pricing (e.g. 'usd')
    """
    pair = f"{base_currency}/{quote_currency}"

    if pair not in PAIRS:
        raise HTTPException(status_code=404, detail="Pair not found")

    prices = service.fetch_prices()

    return Price(pair=pair, price=prices[pair])


@app.get("/api/prices/{base_currency}/{quote_currency}/history")
async def get_price_history(base_currency: str, quote_currency: str) -> PriceHistory:
    """
    Get 24 hour price history for a trading pair.

    Arguments:
        base_currency: the currency being priced (e.g. 'btc')
        quote_currency: the currency used for pricing (e.g. 'usd')
    """
    pair = f"{base_currency}/{quote_currency}"

    if pair not in PAIRS:
        raise HTTPException(status_code=404, detail="Pair not found")

    prices = service.get_price_history(pair)
    rank = service.get_volatility_rank(pair)

    return PriceHistory(pair=pair, prices=prices, volatility_rank=rank)
