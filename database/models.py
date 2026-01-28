from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)  # Telegram User ID
    username = Column(String, nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow)
    plan_expiry = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False)
    
    settings = relationship("Settings", back_populates="user", uselist=False)
    groups = relationship("Group", back_populates="user")
    session = relationship("Session", back_populates="user", uselist=False)

class Session(Base):
    __tablename__ = 'sessions'
    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    session_path = Column(String, nullable=True) # Path to .session file
    phone_number = Column(String, nullable=True)
    api_id = Column(Integer, nullable=True)
    api_hash = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="session")

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    group_id = Column(BigInteger, nullable=False)
    group_name = Column(String, nullable=True)
    is_enabled = Column(Boolean, default=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="groups")

class Settings(Base):
    __tablename__ = 'settings'
    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    interval_minutes = Column(Integer, default=25)
    night_mode_enabled = Column(Boolean, default=True)
    active = Column(Boolean, default=True) # Master switch for user
    last_run = Column(DateTime, nullable=True)
    last_msg_index = Column(Integer, default=0)

    user = relationship("User", back_populates="settings")

class RedeemCode(Base):
    __tablename__ = 'redeem_codes'
    code = Column(String, primary_key=True)
    duration_days = Column(Integer, nullable=False)
    is_used = Column(Boolean, default=False)
    used_by = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MessageLog(Base):
    __tablename__ = 'message_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    group_id = Column(BigInteger)
    message_id = Column(Integer)
    sent_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String) # success, failed
    error_info = Column(String, nullable=True)
