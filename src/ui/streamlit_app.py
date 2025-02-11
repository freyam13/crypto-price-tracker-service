import logging
import time
from datetime import UTC, datetime
from typing import Dict

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import COINGECKO_API_KEY
from src.models.currency import PAIRS
from src.services.price_service import PriceService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
service = PriceService(
    db_url=st.secrets["connections"]["neon"]["url"],
    api_key=COINGECKO_API_KEY,
)


@st.cache_data(ttl=90)
def fetch_and_store_prices() -> Dict[str, float]:
    """
    Fetch current prices and store them in the database.

    NOTE: cached for 90 seconds to give slight buffer between refreshes

    Returns:
        dict mapping pair strings to current prices
    """
    logger.info("Fetching current prices from CoinGecko")

    try:
        prices = service.fetch_prices()
        logger.info("Current prices fetched: %s", prices)

        logger.info("Storing prices in database")
        service.store_prices(prices)

        return prices

    except Exception as e:
        logger.error("Error in fetch cycle: %s", e)
        return {}


def get_current_price(pair: str) -> float:
    """
    Get current price from API.

    Arguments:
        pair: trading pair string

    Returns:
        current price for the pair
    """
    try:
        prices = fetch_and_store_prices()
        return prices[pair]

    except Exception as e:
        st.error(f"Error fetching price: {str(e)}")
        return 0.0


@st.cache_data(ttl=90, show_spinner=False)
def get_price_history(pair: str) -> dict:
    """
    Get price history from API.

    NOTE: cached for 90 seconds to give slight buffer between refreshes

    Arguments:
        pair: trading pair string

    Returns:
        price history data including volatility rank
    """
    try:
        prices = service.get_price_history(pair)
        rank = service.get_volatility_rank(pair)
        now = datetime.now(UTC)
        logger.info(
            "Retrieved price history for %s\nData: %s",
            pair,
            {
                "points": len(prices),
                "time_range": f"{prices[0].timestamp if prices else 'N/A'} to {prices[-1].timestamp if prices else 'N/A'}",
                "current_time": now,
            },
        )
        return {
            "pair": pair,
            "prices": prices,
            "volatility_rank": rank,
            "timestamp": now,
        }

    except Exception as e:
        st.error(f"Error fetching history: {str(e)}")
        return {"pair": pair, "prices": [], "volatility_rank": None}


def main():
    st.set_page_config(
        page_title="Crypto Price & Volatility Tracker", page_icon="📈", layout="wide"
    )
    st.title("Crypto Price & Volatility Tracker")

    # use session state for selected pair and previous prices
    if "selected_pair" not in st.session_state:
        st.session_state.selected_pair = PAIRS[0]

    if "previous_prices" not in st.session_state:
        st.session_state.previous_prices = {}

    ###########
    # Sidebar #
    ###########

    st.sidebar.markdown("### Current Prices")
    header_cols = st.sidebar.columns([2, 3, 1])
    header_cols[0].markdown("**Pair**")
    header_cols[1].markdown("**Price**")
    header_cols[2].markdown("**Rank**")
    st.sidebar.markdown("<hr style='margin: 5px 0px'>", unsafe_allow_html=True)

    current_prices = fetch_and_store_prices()

    old_prices = st.session_state.previous_prices.copy()
    st.session_state.previous_prices = current_prices.copy()

    volatility_ranks = {pair: service.get_volatility_rank(pair) for pair in PAIRS}

    for pair in PAIRS:
        price = current_prices.get(pair, 0.0)
        prev_price = old_prices.get(pair, price)
        price_delta = price - prev_price
        formatted_price = f"${price:,.2f}" if pair.endswith("/usd") else f"{price:,.8f}"
        rank = volatility_ranks.get(pair, 0)

        cols = st.sidebar.columns([2, 3, 1])

        if pair == st.session_state.selected_pair:
            cols[0].markdown(f"**{pair}**")
        else:
            if cols[0].button(pair, key=f"btn_{pair}"):
                st.session_state.selected_pair = pair
                st.rerun()

        if price_delta != 0:
            color = "#00FF00" if price_delta > 0 else "#FF0000"
            cols[1].markdown(
                f'<p style="color: {color}; margin: 0; padding: 0;">{formatted_price}</p>',
                unsafe_allow_html=True,
            )
        else:
            cols[1].markdown(
                f'<p style="margin: 0; padding: 0;">{formatted_price}</p>',
                unsafe_allow_html=True,
            )

        cols[2].text("N/A" if rank == 0 else f"#{rank}")

    st.sidebar.markdown("---")

    with st.sidebar:
        st.write("Auto-refreshing every minute...")
        st.text(f"Last updated: {datetime.now(UTC).strftime('%H:%M:%S')} UTC")
        st.spinner()

    col1 = st.container()

    ########
    # Main #
    ########

    with col1:
        price_cols = st.columns([3, 1])
        price_cols[0].markdown(f"### {st.session_state.selected_pair.upper()}")
        rank = volatility_ranks.get(st.session_state.selected_pair, 0)
        price_cols[1].markdown(
            f"### Volatility Rank: #{rank}" if rank else "### Volatility Rank: N/A"
        )

        current_price = current_prices.get(st.session_state.selected_pair, 0.0)
        prev_price = old_prices.get(st.session_state.selected_pair, current_price)
        price_delta = current_price - prev_price

        st.metric(
            label="Current Price",
            label_visibility="collapsed",
            value=(
                f"${current_price:,.2f}"
                if st.session_state.selected_pair.endswith("/usd")
                else f"{current_price:,.8f}"
            ),
            delta=price_delta if price_delta != 0 else None,
        )

    # clear cache and get price history
    get_price_history.clear()
    history = get_price_history(st.session_state.selected_pair)["prices"]

    if history:
        df = pd.DataFrame(
            [(p.timestamp, p.price) for p in history], columns=["timestamp", "price"]
        )

        st.markdown("### 24 Hour Price History")

        min_price = df["price"].min()
        max_price = df["price"].max()
        price_range = max_price - min_price
        y_min = min_price - (price_range * 0.05)
        y_max = max_price + (price_range * 0.05)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["price"],
                mode="lines",
                name=st.session_state.selected_pair,
            )
        )

        fig.update_layout(
            height=400,
            yaxis=dict(range=[y_min, y_max], title="Price"),
            xaxis=dict(title="Time"),
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    logger.info("Waiting for next update cycle")
    time.sleep(60)
    st.rerun()


if __name__ == "__main__":
    main()
