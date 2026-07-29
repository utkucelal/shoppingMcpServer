from sqlmodel import Session, select

from data.models import engine, Order


def insert_orders(orders):

    with Session(engine) as session:
        statement = select(Order.order_id)
        records = session.exec(statement).fetchall() #registered orderids

        for order in orders:
            if order.get("order_id") not in records:
                obj = Order(order_id=order.get("order_id"),
                            order_date=order.get("order_date"),
                            product_names=", ".join(item["title"] for item in order.get("items", []) if item.get("title"))
                            )
                session.add(obj)

        session.commit()


def fetch_orders():

    with Session(engine) as session:
        statement = select(Order)
        db_orders = session.exec(statement).all()

        orders = []

        for order in db_orders:
            items = []

            if order.product_names:
                items = [{"title": name.strip()} for name in order.product_names.split(",") if name.strip()]

            orders.append({
                "order_id": order.order_id,
                "order_date": order.order_date,
                "items": items
            })

        return orders