from __future__ import annotations

from datetime import datetime


def test_portfolio_lifecycle(client):
    # Create user
    user_resp = client.post("/users/", json={"email": "user@example.com", "auth_provider": "password", "two_factor_enabled": False})
    assert user_resp.status_code == 201
    user_id = user_resp.json()["id"]

    # Create benchmark
    benchmark_resp = client.post("/benchmarks/", json={"symbol": "SP500", "name": "S&P 500", "currency": "USD"})
    assert benchmark_resp.status_code == 201
    benchmark_id = benchmark_resp.json()["id"]

    # Create portfolio
    portfolio_resp = client.post(
        "/portfolios/",
        json={"name": "Retirement", "base_currency": "USD", "user_id": user_id, "benchmark_id": benchmark_id},
    )
    assert portfolio_resp.status_code == 201
    portfolio = portfolio_resp.json()

    # Create account
    account_resp = client.post(
        "/accounts/",
        json={
            "portfolio_id": portfolio["id"],
            "broker": "IBKR",
            "account_name": "IBKR-1",
            "type": "broker",
            "currency": "USD",
        },
    )
    assert account_resp.status_code == 201
    account_id = account_resp.json()["id"]

    # Create asset
    asset_resp = client.post(
        "/assets/",
        json={
            "symbol": "AAPL",
            "isin": "US0378331005",
            "name": "Apple Inc",
            "type": "stock",
            "sector": "Technology",
            "region": "US",
            "currency": "USD",
        },
    )
    assert asset_resp.status_code == 201
    asset_id = asset_resp.json()["id"]

    # Record transactions
    buy_resp = client.post(
        "/transactions/",
        json={
            "account_id": account_id,
            "asset_id": asset_id,
            "type": "BUY",
            "qty": "10",
            "price": "150",
            "fee": "1",
            "tax": "0",
            "gross_amount": "1500",
            "trade_currency": "USD",
            "fx_rate_to_portfolio_ccy": 1.0,
            "trade_time": datetime.utcnow().isoformat(),
        },
    )
    assert buy_resp.status_code == 201

    sell_resp = client.post(
        "/transactions/",
        json={
            "account_id": account_id,
            "asset_id": asset_id,
            "type": "SELL",
            "qty": "5",
            "price": "180",
            "fee": "1",
            "tax": "0",
            "gross_amount": "900",
            "trade_currency": "USD",
            "fx_rate_to_portfolio_ccy": 1.0,
            "trade_time": datetime.utcnow().isoformat(),
        },
    )
    assert sell_resp.status_code == 201

    # Record dividend
    dividend_resp = client.post(
        "/dividends/",
        json={
            "account_id": account_id,
            "asset_id": asset_id,
            "ex_date": "2023-01-01",
            "pay_date": "2023-01-15",
            "gross": "10",
            "withholding_tax": "1",
            "net": "9",
            "currency": "USD",
        },
    )
    assert dividend_resp.status_code == 201

    # Add price
    price_resp = client.post(
        "/prices/",
        json={
            "asset_id": asset_id,
            "date": "2023-12-31",
            "close": "190",
            "currency": "USD",
            "source": "test",
        },
    )
    assert price_resp.status_code == 201

    # Portfolio performance
    perf_resp = client.get(f"/portfolios/{portfolio['id']}/performance")
    assert perf_resp.status_code == 200
    performance = perf_resp.json()

    assert performance["portfolio_id"] == portfolio["id"]
    assert performance["dividends_received"] == 9.0
    assert performance["current_value"] > 0
