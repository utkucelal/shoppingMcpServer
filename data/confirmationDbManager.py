from datetime import datetime

from sqlmodel import Session, select

from data.models import engine, PendingConfirmation


def save_pending_confirmation(hash_code, pin, order_details):
    with Session(engine) as session:
        pc = PendingConfirmation(
            hash= hash_code,
            pin = pin,
            product_details = order_details.get("urun", ""),
            price = order_details.get("toplam", ""),
            fees = order_details.get("fees", ""),
            address = order_details.get("adres", ""),
            payment_method = order_details.get("odeme_yontemi", ""),
            status = "pending",
            created_at = datetime.now()
        )
        session.add(pc)
        session.commit()

def get_pending_confirmation(hash_code: str):

    with Session(engine) as session:
        statement = select(PendingConfirmation).where(PendingConfirmation.hash == hash_code)

        record = session.exec(statement).first()

        if record:
            return record.model_dump()

        return None

def confirm_order(hash_code, pin):
    with Session(engine) as session:
        statement = select(PendingConfirmation).where(PendingConfirmation.hash == hash_code)
        row = session.exec(statement).first()

    """Verify PIN and mark order as confirmed (not yet placed)."""

    if not row:
        return False, "Confirmation not found"

    stored_pin, status = row

    if status != "pending":
        return False, "Order already confirmed or completed"

    if stored_pin != pin:
        return False, "Invalid PIN"

    with Session(engine) as session:
        statement = select(PendingConfirmation).where(PendingConfirmation.hash == hash_code)
        order = session.exec(statement).first()
        if order:
            order.status = "confirmed"
            order.confirmed_at = datetime.now()
            session.add(order)
            session.commit()

    return True, "Order confirmed"

def complete_order(hash_code, order_id):
    with Session(engine) as session:
        statment = select(PendingConfirmation).where(PendingConfirmation.hash == hash_code)
        order = session.exec(statment).first()
        if order:
            order.status = "completed"
            order.order_id = order_id
            session.add(order)
            session.commit()