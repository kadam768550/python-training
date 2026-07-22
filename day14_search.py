# day 14)search
import sqlite3
from flask import Flask, render_template, request

app = Flask(__name__)
app.secret_key = 'my secret key'

#Same 2 functions as before
def get_db():
    conn = sqlite3.connect('practise.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        marks INTEGER DEFAULT 0
        subject TEXT NOT NULL,
        attendance INTEGER DEFAULT 0
    )''')
    
    conn.execute("INSERT OR IGNORE INTO products (name, category, price, stock) VALUES ('Laptop', 'Electronics', 55000, 10)")
    conn.execute("INSERT OR IGNORE INTO products (name, category, price, stock) VALUES ('Mobile Phone', 'Electronics', 20000, 15)")
    conn.execute("INSERT OR IGNORE INTO products (name, category, price, stock) VALUES ('Mouse', 'Accessories', 500, 30)")
    conn.execute("INSERT OR IGNORE INTO products (name, category, price, stock) VALUES ('Scanner', 'Office', 7000, 6)")
    conn.execute("INSERT OR IGNORE INTO products (name, category, price, stock) VALUES ('Printer', 'Office', 9000, 7)")
    conn.commit()
    conn.close()