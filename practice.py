import sqlite3
from flask import Flask, render_template, request, redirect, flash, url_for

app = Flask(__name__)
app.secret_key = 'my secret key'  

def get_db():
    connection = sqlite3.connect('practice.db')
    conn.row_factory = sqlite3.Row  
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

    @app.route("/")
    def home():
        conn = get_db()
        products = conn.execute("SELECT * FROM products").fetchall()
        conn.close()
        return render_template("home.html", products=products)
    
    def add_product():
     if request.method == "POST":
        new_product = {
            "id": len(products) + 1,
            "name": request.form["name"],
            "category": request.form["category"],
            "price": int(request.form["price"]),
            "stock": int(request.form["stock"])
        }

        if not new_product["name"] or not new_product["category"] or new_product["price"] <= 0 or new_product["stock"] < 0:
            flash("Please fill in all fields correctly.", "error")
            return render_template("add_product.html")
        
        conn = get_db()
        conn.execute(''' INSERT INTO products 
                    (name, category, price, stock) VALUES (?, ?, ?, ?)''', 
                    (new_product["name"], new_product["category"], new_product["price"], new_product["stock"]))
       
        conn.commit()
        conn.close()

        # Flash message to user
        flash("Product added successfully!", "success")
    
    return render_template("product.html", products=products)

    return render_template("add_product.html")

@app.route('/delete/<int:id>')
def delete_product(id):
   conn = get_db()

   product = conn.execute('DELETE FROM products WHERE id = ?', (id,))
   conn.commit()
   conn.close()

   flash(f"{product['name']} deleted", 'success')
   return redirect(url_for('product_page'))


        



