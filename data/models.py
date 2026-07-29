from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Session, select, create_engine
from pathlib import Path


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    order_id: str = Field(primary_key=True)
    order_date: Optional[str] = None
    product_names: Optional[str] = None


class PendingConfirmation(SQLModel, table=True):
    __tablename__ = "pending_confirmations"

    hash: str = Field(primary_key=True)
    pin: str
    product_details: str
    price: str
    fees: str
    address: str
    payment_method: str
    created_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    status: str
    order_id: Optional[str] = None


BASE_DIR = Path(__file__).resolve().parent

db_path = BASE_DIR / "main.db"
sqlite_url = f"sqlite:///{db_path}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    create_db_and_tables()
