from fastapi import APIRouter
from app.api.endpoints import auth, portfolios, accounts, transactions, dividends, imports, analytics, broker_imports

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(portfolios.router, prefix="/portfolios", tags=["portfolios"])
api_router.include_router(accounts.router, prefix="/portfolios/{portfolio_id}", tags=["accounts"])
api_router.include_router(transactions.router, prefix="/accounts/{account_id}", tags=["transactions"])
api_router.include_router(dividends.router, prefix="/accounts/{account_id}", tags=["dividends"])
api_router.include_router(imports.router, prefix="/import", tags=["import"])
api_router.include_router(analytics.router, prefix="/portfolios/{portfolio_id}/analytics", tags=["analytics"])
api_router.include_router(broker_imports.router, prefix="/brokers", tags=["brokers"])