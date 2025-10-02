from __future__ import annotations

from fastapi import FastAPI

from .database import Base, engine
from .routers import (
    accounts,
    assets,
    benchmarks,
    dividends,
    imports,
    portfolios,
    transactions,
    users,
    prices,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Stock Portfolio Platform", version="0.1.0")

app.include_router(portfolios.router)
app.include_router(accounts.router)
app.include_router(assets.router)
app.include_router(transactions.router)
app.include_router(dividends.router)
app.include_router(benchmarks.router)
app.include_router(imports.router)
app.include_router(users.router)
app.include_router(prices.router)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
