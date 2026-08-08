import os
import sqlite3
from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = "my secret key"

#Absoulute path - Always with app.py folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'myproject.db')
# 2 functions
def get_db():
    """Database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # To access columns by name
    return conn

def init_db():
    """Create tables"""
    conn = get_db()

    # Products table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    try:
        conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'product'")
    except Exception:
        # Column already exists
        pass

    try:
        conn.execute("ALTER TABLE products ADD COLUMN photo TEXT DEFAULT 'default.jpg'")
    except Exception:
        # Column already exists
        pass

    # Categories table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # Default categories
    default_categories = [
        "Laptop",
        "Mobile",
        "Accessories",
        "Monitors",
        "Printers",
        "Storage",
        "Networking",
        "Electronics",
        "Wearable",
        "Office",
        "Furniture"
    ]

    for category in default_categories:
        try:
            conn.execute(
                "INSERT INTO categories (name) VALUES (?)",
                (category,)
            )
        except sqlite3.IntegrityError:
                # Subject already exists, ignore the error
            pass

    conn.commit()
    conn.close()
init_db()  # Initialize the database

if __name__ == "__main__":
    app.run(debug=True)