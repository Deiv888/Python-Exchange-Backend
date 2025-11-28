from .database import Base
from sqlalchemy import TIMESTAMP, Column, Integer, Numeric, String, Boolean, text, ForeignKey, Double
from sqlalchemy.orm import relationship

#tabella utenti
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    wallets = relationship("Wallet", back_populates="owner")

#tabella wallet
class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    valuta = Column(String, nullable=False)
    balance = Column(Numeric(20, 8), nullable=False, server_default="0")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    owner = relationship("User", back_populates="wallets")
    transactions = relationship("Transaction", back_populates="wallet")

#tabella transactions
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, nullable=False)
    wallet_id = Column(Integer, ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False)
    asset = Column(String, nullable=False)
    type = Column(String, nullable=False)
    quantità = Column(Numeric(20, 8), nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    wallet = relationship("Wallet", back_populates="transactions")