from sqlalchemy import Boolean, Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

from app.db.base import Base
from app.models.base import BaseModel


class User(Base, BaseModel):
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    is_superuser = Column(Boolean, nullable=False, default=False, server_default=text("false"))
    auth_provider = Column(String(50), nullable=False, default="email", server_default=text("'email'"))
    two_factor_enabled = Column(Boolean, nullable=False, default=False, server_default=text("false"))