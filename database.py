import sqlite3
from config import DB_PATH
 
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def initialize_db():
    with get_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            brand TEXT,
            url TEXT UNIQUE NOT NULL,
            description TEXT,
            created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price REAL NOT NULL,
            checked_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
        """)

def add_product(name, brand, url, description=None):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO products (name, brand, url, description)
            VALUES (?, ?, ?, ?)
            """,
            (name, brand, url, description)
        )
        return cursor.lastrowid


def add_price(product_id, price):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO price_history (product_id, price)
            VALUES (?, ?)
            """,
            (product_id, price)
        )


def get_all_products():
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM products")
        return cursor.fetchall()