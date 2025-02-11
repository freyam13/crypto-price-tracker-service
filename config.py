import os

import streamlit as st

# environment-based configuration
try:
    DB_URL = os.getenv("DATABASE_URL") or st.secrets["connections"]["neon"]["url"]

except (AttributeError, KeyError):
    raise ValueError(
        "Database URL must be provided via DATABASE_URL environment variable "
        "or Streamlit secrets"
    )

# use demo key for development
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "demo-key")

# API configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_URL = f"http://{API_HOST}:{API_PORT}/api"
