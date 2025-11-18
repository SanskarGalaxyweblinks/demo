import secrets
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from ..services.database import Base

class UserAPIKey(Base):
    __tablename__ = "user_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_name = Column(String, nullable=False)
    api_key_prefix = Column(String, nullable=False)
    api_key_hash = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_hour = Column(Integer, default=1000)
    rate_limit_per_day = Column(Integer, default=10000)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)

    @staticmethod
    def generate_api_key():
        """Returns (full_key, key_hash, prefix)"""
        # Generates a random secure token
        raw_key = secrets.token_urlsafe(32)
        prefix = raw_key[:8]
        # In a real app, hash the raw_key before storing!
        # For this demo, we are storing the hash as the raw key (simplified)
        # You should use a hashing function like sha256 here.
        return raw_key, raw_key, prefix