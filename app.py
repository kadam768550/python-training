from mimetypes import init

from flask import Flask, render_template, request, redirect, flash, url_for

from database import get_db, init_db # Importing the database connection function

app = Flask(__name__)
app.secret_key = 'My Secret Key' #Needed for flashing messages

products = [
    {
        "id": 1,
        "name": "Laptop",
        "category": "Electronics",
        "price": 55000,
        "stock": 10
    },
    {
        "id": 2,
        "name": "Mobile",
        "category": "Electronics",
        "price": 20000,
        "stock": 15
    },
    {
        "id": 3,
        "name": "Keyboard",
        "category": "Accessories",
        "price": 800,
        "stock": 25
    },
    {
        "id": 4,
        "name": "Mouse",
        "category": "Accessories",
        "price": 500,
        "stock": 30
    },
    {
        "id": 5,
        "name": "Printer",
        "category": "Office",
        "price": 12000,
        "stock": 5
    }
]

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/orders")
def orders():
    return render_template("orders.html")


@app.route("/products")
def product():
    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("product.html", products=products)

@app.route("/edit/<int:id>")
def edit_product(id):
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    conn.close()

    if product is None:
        flash("Product not found.", "danger")
        return render_template("product.html", products=products)

    return render_template("detail.html", product=product)


@app.route("/add_product", methods=["GET", "POST"])
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
        

        products.append(new_product)
        # Flash message to user
        flash("Product added successfully!", "success")
        print("Updated Products List:", products)  # Debugging line to check the updated products list
        return render_template("product.html", products=products)

    return render_template("add_product.html")

#DELETE - remove by ID
@app.route('/delete/<int:id>')
def delete_product(id):
    conn = get_db()

    # First Check if it exists
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    if product is None:
        flash("Product not found.", "danger")
        conn.close()
        return render_template("product.html", products=products)

    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash("Product deleted successfully!", "success")
    return redirect(url_for('product'))


@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    init_db()  # Initialize the database
    app.run(debug=True)