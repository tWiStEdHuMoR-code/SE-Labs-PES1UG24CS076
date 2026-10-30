"""Supplier purchase order tracker for a stores department."""
import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

CREATE_TABLE_SQL = (
    "CREATE TABLE orders ("
    "id INTEGER PRIMARY KEY, supplier TEXT, item TEXT, "
    "quantity INTEGER, received INTEGER)"
)


def place_order(conn, supplier, item, quantity):
    """Insert a new order and return the total quantity ordered so far."""
    conn.execute(
        "INSERT INTO orders (supplier, item, quantity, received) "
        "VALUES (?, ?, ?, 0)",
        (supplier, item, quantity),
    )
    return conn.execute("SELECT SUM(quantity) FROM orders").fetchone()[0]


def mark_received(conn, order_id, remarks):
    """Mark an order as received and log the remarks."""
    conn.execute("UPDATE orders SET received = 1 WHERE id = ?", (order_id,))
    logging.info("Order %s received: %s", order_id, remarks)


def notify_warehouse(supplier):
    """Notify the warehouse about a supplier delivery."""
    print("notifying warehouse about " + supplier)


def cleanup(conn):
    """Delete fulfilled orders."""
    try:
        conn.execute("DELETE FROM orders WHERE received = 1")
    except sqlite3.Error as err:
        logging.error("Cleanup failed: %s", err)


def pending_count(conn):
    """Return the number of orders not yet received."""
    return conn.execute(
        "SELECT COUNT(*) FROM orders WHERE received = 0"
    ).fetchone()[0]


def main():
    """Run a short demonstration."""
    conn = sqlite3.connect(":memory:")
    conn.execute(CREATE_TABLE_SQL)
    place_order(conn, "Acme Steel", "rods", 40)
    order_total = place_order(conn, "Bolt Co", "bolts", 500)
    mark_received(conn, 1, "ok")
    notify_warehouse("Acme")
    print(pending_count(conn), order_total)
    cleanup(conn)
    conn.close()


if __name__ == "__main__":
    main()
