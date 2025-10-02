# Stock App

This repository implements the initial backend service for the multi-broker investment tracking platform alongside a detailed product requirements document. Refer to [docs/product-requirements.md](docs/product-requirements.md) for the full specification.

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is built with FastAPI and exposes CRUD endpoints for users, portfolios, accounts, assets, transactions, dividends, benchmarks, prices, and CSV imports. Once the server is running you can access the interactive API docs at `http://127.0.0.1:8000/docs`.

## Running tests

```bash
pip install -r requirements.txt
pip install pytest
pytest
```
