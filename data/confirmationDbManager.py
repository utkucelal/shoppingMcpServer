import sqlite3
import json


def init_confirmation_db(db_path="data/confirmations.db"):
    """Initialize the confirmations database with pending_confirmations table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_confirmations (
            hash TEXT PRIMARY KEY,
            pin TEXT NOT NULL,
            product_details TEXT NOT NULL,
            price TEXT,
            fees TEXT,
            address TEXT,
            payment_method TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confirmed_at TIMESTAMP,
            status TEXT DEFAULT 'pending',
            order_id TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_pending_confirmation(hash_code, pin, order_details, db_path="data/confirmations.db"):
    """Save pending confirmation with order details and PIN to database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    product_details = order_details.get("urun", "")
    price = order_details.get("toplam", "")
    address = order_details.get("adres", "")
    payment_method = order_details.get("odeme_yontemi", "")
    fees = order_details.get("fees", "")

    cursor.execute("""
        INSERT INTO pending_confirmations 
        (hash, pin, product_details, price, fees, address, payment_method, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (hash_code, pin, product_details, price, fees, address, payment_method))

    conn.commit()
    conn.close()


def get_pending_confirmation(hash_code, db_path="data/confirmations.db"):
    """Retrieve pending confirmation by hash."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT hash, pin, product_details, price, fees, address, payment_method, status, order_id, created_at
        FROM pending_confirmations
        WHERE hash = ?
    """, (hash_code,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "hash": row[0],
            "pin": row[1],
            "product_details": row[2],
            "price": row[3],
            "fees": row[4],
            "address": row[5],
            "payment_method": row[6],
            "status": row[7],
            "order_id": row[8],
            "created_at": row[9]
        }
    return None


def confirm_order(hash_code, pin, db_path="data/confirmations.db"):
    """Verify PIN and mark order as confirmed (not yet placed)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT pin, status FROM pending_confirmations WHERE hash = ?
    """, (hash_code,))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return False, "Confirmation not found"

    stored_pin, status = row

    if status != "pending":
        conn.close()
        return False, "Order already confirmed or completed"

    if stored_pin != pin:
        conn.close()
        return False, "Invalid PIN"

    cursor.execute("""
        UPDATE pending_confirmations
        SET status = 'confirmed', confirmed_at = CURRENT_TIMESTAMP
        WHERE hash = ?
    """, (hash_code,))

    conn.commit()
    conn.close()

    return True, "Order confirmed"


def complete_order(hash_code, order_id, db_path="data/confirmations.db"):
    """Mark order as completed with order ID."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE pending_confirmations
        SET status = 'completed', order_id = ?
        WHERE hash = ?
    """, (order_id, hash_code))

    conn.commit()
    conn.close()
