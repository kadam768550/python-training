import sqlite3
from flask import Flask, render_template, request, flash
app = Flask(__name__)
app.secret_key = 'my secret key'

# 2 functions
def get_db():
    """Database connection"""
    conn = sqlite3.connect('myproject.db')
    conn.row_factory = sqlite3.Row # To access columns by name
    return conn

def init_db():
    """Create table"""
    conn = get_db()
    # Create products table if it doesn't exist
    conn.execute('''
                 CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock INTEGER NOT NULL
                 )
                    ''')
    
    conn.execute('''
                 CREATE TABLE IF NOT EXISTS users (
                 
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                 )
                    ''')    
    
    conn.commit()
    conn.close()

    if __name__ == "__main__":
     init_db() # Initialize the database
     app.run(debug=True)
