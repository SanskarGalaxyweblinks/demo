import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from ..services.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth_id = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    organization_name = Column(String)
    
    # Usage Tracking
    document_classifier_count = Column(Integer, default=0)
    email_classifier_count = Column(Integer, default=0)
    
    email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    email_verification_token_expires = Column(DateTime, nullable=True)
    
    password_reset_token = Column(String, nullable=True)
    password_reset_token_expires = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)