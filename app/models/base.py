from datetime import datetime
import uuid
from sqlalchemy import Column, DateTime, text
from sqlalchemy.dialects.postgresql import UUID

class BaseModel:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("uuid_generate_v4()"))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=text("now()"), onupdate=datetime.utcnow)