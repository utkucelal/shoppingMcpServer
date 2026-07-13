import sqlite3
import json


def init_db(db_path="data/orders.db"):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            order_date TEXT,
            product_names TEXT
        )
    """)

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


def insert_orders(orders, db_path="data/orders.db"):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT order_id FROM orders")
    currentOrders = cursor.fetchall()

    for order in orders:
        order_id = order.get("order_id")
        order_date = order.get("order_date")
        product_names = ", ".join(item["title"] for item in order.get("items", []) if item.get("title"))

        if order_id not in currentOrders:

            cursor.execute("""
            INSERT INTO orders (order_id, order_date, product_names)
            VALUES (?, ?, ?)
            ON CONFLICT(order_id) DO UPDATE SET
                order_date = excluded.order_date,
                product_names = excluded.product_names
            """, (order_id, order_date, product_names))

    conn.commit()
    conn.close()


def fetch_orders(db_path="data/orders.db"):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT order_id, order_date, product_names FROM orders")
    rows = cursor.fetchall()
    conn.close()

    orders = []
    for order_id, order_date, product_names in rows:
        items = []
        if product_names:
            items = [{"title": name.strip()} for name in product_names.split(",") if name.strip()]

        orders.append({
            "order_id": order_id,
            "order_date": order_date,
            "items": items
        })

    return orders