from mimetypes import init

from flask import Flask, abort, redirect, render_template, request, flash, url_for

from database import get_db, init_db # Importing the database connection function

app = Flask(__name__)
app.secret_key = 'My Secret Key' #Needed for flashing messages

products = [
    {
        "name": "Laptop",
        "category": "Electronics",
        "price": 55000,
        "stock": 10
    },
    {
        "name": "Mobile",
        "category": "Electronics",
        "price": 20000,
        "stock": 15
    },
    {
        "name": "Keyboard",
        "category": "Accessories",
        "price": 800,
        "stock": 25
    },
    {
        "name": "Mouse",
        "category": "Accessories",
        "price": 500,
        "stock": 30
    },
    {
        "name": "Printer",
        "category": "Office",
        "price": 12000,
        "stock": 5
    }
]

@app.route("/")
def home():
    conn = get_db()

    #All products from database
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    
    #Stats using count
    total = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    return render_template("home.html", products=products, total=total)

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
    return render_template("products.html", products=products)

#DELETE - remove by ID
@app.route('/delete/<int:id>')
def delete_product(id):
    conn = get_db()

    # First Check if it exists
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()
    if product is None:
        flash("Product not found.", "danger")
        conn.close()
        return redirect(url_for('product'))

    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash("Product deleted successfully!", "success")
    return redirect(url_for('product'))

@app.route("/products/<int:id>")
def product_detail(id):
    conn = get_db()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (id,)).fetchone()
    conn.close()

    if product is None:
        flash("Product not found.", "danger")
        return redirect(url_for("product")) #Function name of your products page

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

        # Flash message to user
        flash("Product added successfully!", "success")
        print("Updated Products List:", products)  # Debugging line to check the updated products list
        return redirect(url_for("product"))

    return render_template("add_product.html")

    #EDIT - update by ID
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = get_db()

    if request.method == 'POST':
        name = request.form['product_name']
        category = request.form['category']
        price = request.form['price']
        stock = request.form['stock']

        if not name:
            flash('Name cannot be empty','danger')
            return redirect(url_for('edit_product',id=id))

        # UPDATE record
        conn.execute("""
            UPDATE products
            SET name = ?, category = ?, price = ?, stock = ?
            WHERE id = ?
        """, (name, category, price, stock, id))

        conn.commit()
        conn.close()

        flash(f'{name} updated successfully!', "success")
        return redirect(url_for('product'))
    
    #GET - fetch exisiting record
    product = conn.execute('SELECT * FROM products WHERE id = ?',(id,)).fetchone()
    conn.close()

    if product is None:
        abort(404) # trigger 404.html

    return render_template("edit_product.html", product=product) 

@app.route("/search")
def search():
    #step 1 - get query from URL
    q = request.args.get('q','')
    # request.args - GET parameters
    # 'q' - Form  - name = 'q'
    conn = get_db()
    
    if q:
        products = conn.execute('''SELECT * FROM products 
                                WHERE name LIKE ? 
                                OR category LIKE ?
                                OR price LIKE ?
                                OR stock LIKE ?''',
                                (f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%')).fetchall()
        
    else:
        products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()
    return render_template("search.html", products=products, query=q)

@app.route("/filter")
def filter_products():
    conn = get_db()

    category = request.args.get("category", "")
    min_price = request.args.get("min_price", "")
    max_price = request.args.get("max_price", "")

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if min_price:
        query += " AND price >= ?"
        params.append(min_price)

    if max_price:
        query += " AND price <= ?"
        params.append(max_price)

    query += " ORDER BY id DESC"

    products = conn.execute(query, params).fetchall()

    # Category list for dropdown
    categories = conn.execute(
        "SELECT DISTINCT category FROM products"
    ).fetchall()

    conn.close()

    return render_template(
        "filter.html",
        products=products,
        categories=categories,
        selected_category=category,
        min_price=min_price,
        max_price=max_price
    )

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    init_db()  # Initialize the database
    app.run(debug=True)