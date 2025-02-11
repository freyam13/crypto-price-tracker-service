# Crypto Price Tracker

## Overview

A production-ready service for tracking cryptocurrency prices in real-time. This project demonstrates my ability to build robust, scalable backend services with modern Python practices and tools. The service provides:

- real-time crypto price data updates from CoinGecko API
- historical price tracking and storage
- volatility analysis and ranking
- REST API endpoints for data access
- interactive web UI for visualization

### Features and Implementation

- real-time price updates via CoinGecko API
- PostgreSQL for time-series price data storage
- REST API built with FastAPI
- clean, responsive UI built with Streamlit
- efficient database queries with proper indexing
- Plotly for interactive charts
- handles API rate limiting and connection errors gracefully
- calculates volatility rankings using standard deviation

### Implementation Details

1. **Architecture**:
    - FastAPI for REST API endpoints
    - PostgreSQL for reliable data storage
    - SQLAlchemy for database operations
    - Streamlit UI as a bonus feature

2. **Implementation Strategy**:
    - API-first development approach with FastAPI
    - modular code structure with clear separation of concerns
    - type hints and docstrings for better maintainability
    - basic error handling and logging
    - multi-layer caching strategy (LRU + Streamlit)
    - SQL queries optimized for time-series data
    - modern Python practices (type hints, dataclasses)
    - focused on core functionality with room for expansion

3. **Separation of Concerns**:
    - core business logic lives in the `PriceService` class
    - data models are independent of presentation
    - API layer can run independently of UI
    - database operations are isolated from business logic

4. **Extensibility**:
    - same service powers both REST API and UI
    - new frontends can be added without modifying core logic
    - additional data sources could be added by implementing new services
    - API-first design allows for easy integration with other systems

5. **Performance Optimizations**:
    - LRU caching for expensive database operations
    - Streamlit component caching for UI responsiveness
    - grouped CoinGecko API calls by currency

    The LRU (Least Recently Used) cache was introduced to solve performance bottlenecks
    when fetching historical price data and calculating volatility rankings. These
    operations require complex database queries that were being executed repeatedly
    when users interacted with the UI. The cache stores the results of these queries
    for a short period, significantly improving UI responsiveness while maintaining
    data freshness.

    Key benefits:
      - reduced database load
      - faster UI response times
      - better user experience
      - maintained data accuracy with appropriate cache timeouts

2. **Data Flow**:
     ```
                      ┌─────────────┐
                      │ Streamlit UI│
                      └──────┬──────┘
                             │
    ┌───────────┐    ┌──────┴───────┐    ┌──────────┐
    │ CoinGecko │───►│ FastAPI      │───►│PostgreSQL│
    │ API       │    │ Service      │    │          │
    └───────────┘    └──────────────┘    └──────────┘
     ```

3. **Key Components**:
   - price service: core business logic
   - database schema: time-series storage
   - REST API: clean interface
   - UI: visualization

### Production Considerations and Future Improvements

Current limitations and potential improvements for a production environment:

1. **Data Collection and Processing**:

    current limitations:
      - CoinGecko's free tier rate limits
      - one-minute polling misses price movements
      - no redundancy for API failures

    improvements:
      - use WebSocket connections for live price feeds
      - implement message queues (Kafka/RabbitMQ) for event streaming
      - add async processing for non-critical updates
          - add retry mechanisms and circuit breakers

2. **Storage and Performance**:

    current limitations:
      - single database instance
      - 24-hour price history limit
      - depends on Neon's free tier

    improvements:
      - switch to specialized time-series databases
      - pre-calculate statistics in materialized views
      - implement proper database sharding strategy
      - set up read replicas for query optimization

3. **Caching and Scalability**:

    current limitations:
      - no distributed caching
      - limited request handling

    improvements:
      - multi-layer caching strategy (Redis, CDN)
      - pre-aggregate common calculations
      - implement request rate limiting
      - add geographic data distribution
          - add load balancing

4. **Infrastructure and Monitoring**:

    current limitations:
      - basic error handling
      - minimal logging

    improvements:
      - auto-scaling based on traffic patterns
      - multi-region deployment
      - proper failover and disaster recovery
      - advanced monitoring and alerting

5. **Feature Enhancements**:
    - add more trading pairs
    - implement technical indicators
    - add data export capabilities
    - add user preferences
    - improve UI customization

### Testing Strategy

Current test coverage includes:
  - unit tests for core service logic
  - basic API endpoint tests

To extend:
  - add integration tests
  - add performance tests
  - add end-to-end tests

## Features

- real-time price updates for multiple cryptocurrency pairs
- 24-hour price history charts
- volatility ranking system
- clean, responsive UI built with Streamlit
- PostgreSQL database for reliable data storage

## Prerequisites

- Python 3.11+
- Pipenv
- PostgreSQL database (required for production, provided through Neon)
- CoinGecko API key

## Deployment

To deploy this app publicly, you'll need to configure the following secrets in your Streamlit Cloud dashboard:

```toml
[connections.neon]
url = "your-neon-database-url"

COINGECKO_API_KEY = "your-coingecko-api-key"
```

NOTE: These secrets should never be committed to the repository.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd monte-carlo
```

2. Install dependencies using Pipenv:
```bash
pipenv install
```

3. Configure secrets:
   - copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
   - update with your credentials:
```toml
[connections.neon]
url = "postgresql://user:pass@host:port/dbname"

[api]
host = "localhost"
port = 8000
coingecko_key = "your-api-key-here"
```

## Running the Application

1. Start both the API and UI services:
```bash
pipenv run python run.py
```

This will start:
- FastAPI server at http://localhost:8000
- Streamlit UI at http://localhost:8501

Alternatively, you can run services individually:

- API only:
```bash
pipenv run python -m src.run --api-only
```

- UI only:
```bash
pipenv run python -m src.run --ui-only
```

## Using the API

The API provides several endpoints:

1. View API documentation:
   - interactive OpenAPI docs: http://localhost:8000/docs
   - ReDoc alternative: http://localhost:8000/redoc

2. Get current price:
   ```bash
   # format: /api/prices/{base_currency}/{quote_currency}/current
   # example: Get the current price of Bitcoin in USD
   curl http://localhost:8000/api/prices/btc/usd/current
   ```

   response:
   ```json
   {
     "pair": "btc/usd",
     "price": 48350.52
   }
   ```

3. Get price history with volatility rank:
   ```bash
   # Format: /api/prices/{base_currency}/{quote_currency}/history
   # Example: Get 24h price history for Bitcoin in USD
   curl http://localhost:8000/api/prices/btc/usd/history
   ```

   Response:
   ```json
   {
     "pair": "btc/usd",
     "prices": [
       {
         "timestamp": "2025-02-12T12:00:00Z",
         "price": 48350.52
       },
       ...
     ],
     "volatility_rank": 1
   }
   ```

Where:
- `base_currency`: the currency being priced (e.g. btc, eth, sol)
- `quote_currency`: the currency used for pricing (e.g. usd, eur)
- `volatility_rank`: position in volatility ranking (1 = most volatile)

## Using the UI

The Streamlit UI provides a user-friendly interface for:

- real-time price updates
- 24-hour price charts
- volatility rankings
- multiple cryptocurrency pairs

Access the UI at http://localhost:8501

### UI Screenshot

![Crypto Price & Volatility Tracker UI](resources/ui-screenshot.png)
**NOTE**: This is a screenshot of the UI running on my local machine; pardon the janky data.

The UI features:
- left sidebar: current prices table with volatility rankings
- main view:
  - selected pair details with current price and volatility rank
  - 24-hour interactive price chart
- auto-refreshing data every minute

## Project Structure

```
├── src/
│   ├── api/           # FastAPI endpoints
│   ├── db/            # database operations
│   ├── models/        # data models
│   ├── services/      # business logic
│   └── ui/            # Streamlit interface
├── tests/
│   ├── conftest.py    # test configuration
│   └── services/      # service tests
├── .streamlit/
│   └── secrets.toml   # configuration secrets (not in VCS)
├── config.py          # configuration and deployment settings
├── run.py             # application runner
├── Pipfile            # Python dependencies
└── README.md          # documentation
```

## Development

First time setup:
```bash
pipenv install --dev
pipenv run pre-commit install
```

### Pre-Commit Hooks

This project uses pre-commit hooks to ensure code quality and consistency. To set up the development environment:

1. Install pre-commit:
   ```bash
   pip install pre-commit
   ```

2. Install the git hooks:
   ```bash
   pre-commit install
   ```

The following hooks will run automatically on every commit:

- [**black**](https://black.readthedocs.io/): Code formatting
- [**isort**](https://pycqa.github.io/isort/): Import sorting
- [**ruff**](https://beta.ruff.rs/docs/): Linting and formatting
- [**mypy**](https://mypy.readthedocs.io/): Type checking
- [**pre-commit-hooks**](https://pre-commit.com/hooks.html): Common git hooks (trailing whitespace, YAML checks, etc.)

You can run the hooks manually:

```bash
# run on all files
pre-commit run --all-files

# run on staged files
pre-commit run
```

These can also be run individually/manually:

```bash
pipenv run black .
pipenv run isort .
pipenv run ruff check .
pipenv run ruff format .
```
