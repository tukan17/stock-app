from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    auth_provider: str = "email"
    two_factor_enabled: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class User(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PortfolioBase(BaseModel):
    name: str
    base_currency: str
    benchmark_id: Optional[uuid.UUID] = None


class PortfolioCreate(PortfolioBase):
    pass


class PortfolioUpdate(PortfolioBase):
    pass


class Portfolio(PortfolioBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountBase(BaseModel):
    name: str
    broker: str
    type: str
    currency: str


class AccountCreate(AccountBase):
    portfolio_id: uuid.UUID


class AccountUpdate(AccountBase):
    pass


class Account(AccountBase):
    id: uuid.UUID
    portfolio_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True