import sqlite3
from datetime import datetime 

db_path = 'data/price_tracker.db'

def connection():
    return sqlite3.connect(db_path)

def db_initialization():
    con = connection()
    cur = con.cursor()
    cur.execute("CREATE TABLE products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, brand TEXT NOT NULL, url TEXT NOT NULL, target_price REAL, description TEXT, created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    cur.execute("CREATE TABLE price_history (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id INTEGER, price REAL, checked_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(product_id) REFERENCES products(id))")
    con.commit()
    con.close()

def add_product(name, brand, url, target_price = None, description = None):
    con = connection()
    cur = con.cursor()
    cur.execute("""
    INSERT INTO products (name, brand, url, target_price, description)
    VALUES (?,?,?,?,?)""", (name, brand, url, target_price, description))
    con.commit()
    con.close()

def add_price(product_id, price):
    con = connection()
    cur =  con.cursor()
    cur.execute("""
    INSERT INTO price_history (product_id, price)
    VALUES (?,?)""", (product_id, price))
    con.commit()
    con.close()

def get_last_price(product_id):
    con = connection()
    cur =  con.cursor()
    cur.execute("""
    SELECT price FROM price_history
    WHERE product_id = ?
    ORDER BY checked_time DESC
    LIMIT 1""", (product_id))
    result = cur.fetchone()
    con.close()
    return result[0] if result else None

def get_all_products():
    con = connection()
    cur =  con.cursor()
    cur.execute("""
    SELECT * FROM products""")
    products = cur.fetchall()
    con.close()
    return products