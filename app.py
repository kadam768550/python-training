from http import client

from click import prompt
from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, flash, session, url_for
from datetime import datetime
from database import get_db, init_db
from groq import Groq
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = Flask(__name__)
app.secret_key = 'My Secret Key'

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

products = [
    {"name": "Laptop","category": "Electronics","price": 55000, "stock": 10},
    {"name": "Mobile","category": "Electronics","price": 20000,"stock": 15},
    {"name": "Keyboard","category": "Accessories","price": 800,"stock": 25},
    {"name": "Mouse","category": "Accessories","price": 500,"stock": 30},
    {"name": "Printer","category": "Office","price": 12000,"stock": 5}
]

@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 8
    offset = (page - 1) * per_page
    conn = get_db()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC LIMIT ? OFFSET ?',(per_page, offset)).fetchall()

    total = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    conn.close()
    total_pages = (total + per_page - 1) // per_page

    return render_template("home.html",products=products,page=page,total_pages=total_pages)

@app.route("/products")
def product():
    conn = get_db()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()

    return render_template("products.html",products=products)

@app.route("/products/<int:id>/tip")
def get_ai_tip(id):
    conn = get_db()

    product = conn.execute("SELECT * FROM products WHERE id = ?",(id,)).fetchone()
    conn.close()

    if product is None:abort(404)

    prompt = f"""
    Product Name: {product['name']}
    Category: {product['category']}
    Price: {product['price']}
    Stock: {product['stock']}
    Please provide a tip for selling this product effectively.
    Keep it simple and short in 2-3 lines.
    """

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for the SmartTech Store Management System."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7, # NEW
        max_tokens=80 # Limit the response length
    )
    tip = response.choices[0].message.content
    return render_template("detail.html",product=product,tip=tip)

@app.route('/delete/<int:id>')
def delete_product(id):
    if session.get('role') != 'admin':
        flash(
            "Admins only! You do not have permission",
            "danger")
        return redirect(url_for('home'))

    conn = get_db()
    product = conn.execute('SELECT * FROM products WHERE id = ?',(id,)).fetchone()

    if product is None:
        flash("Product not found.","danger")
        conn.close()
        return redirect(url_for('product'))

    conn.execute(
        'DELETE FROM products WHERE id = ?',(id,))

    conn.commit()
    conn.close()

    flash("Product deleted successfully!","success")
    return redirect(url_for('product'))

@app.route("/products/<int:id>")
def product_detail(id):
    conn = get_db()

    product = conn.execute("SELECT * FROM products WHERE id = ?",(id,)).fetchone()
    conn.close()

    if product is None:
        flash("Product not found.","danger")
        return redirect(url_for("product"))
    return render_template("detail.html",product=product)

@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if session.get('role') != 'admin':
        flash("Admins only! You do not have permission","danger")
        return redirect(url_for('home'))

    if request.method == "POST":
        new_product = {
            "id": len(products) + 1,
            "name": request.form["name"],
            "category": request.form["category"],
            "price": int(request.form["price"]),
            "stock": int(request.form["stock"])
        }

        if (not new_product["name"]or not new_product["category"]or new_product["price"] <= 0 or new_product["stock"] < 0):
            flash("Please fill in all fields correctly.","error")
            return render_template("add_product.html")

        file = request.files.get('photo')
        filename = 'default.png'

        if (
            file and file.filename and allowed_file(file.filename)):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

        conn = get_db()
        conn.execute('''
            INSERT INTO products
            (name, category, price, stock, photo)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (new_product["name"],new_product["category"],new_product["price"],new_product["stock"],filename))

        conn.commit()
        conn.close()

        flash("Product added successfully!","success")
        return redirect(url_for("product"))
    return render_template("add_product.html")

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if session.get('role') != 'admin':
        flash("Admins only! You do not have permission","danger")
        return redirect(url_for('home'))

    conn = get_db()
    if request.method == 'POST':
        name = request.form['product_name']
        category = request.form['category']
        price = request.form['price']
        stock = request.form['stock']

        if not name:
            flash('Name cannot be empty','danger')
            conn.close()

            return redirect(url_for('edit_product',id=id))

        file = request.files.get('photo')
        filename = 'default.png'

        if (file and file.filename and allowed_file(file.filename)):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))

        conn.execute('UPDATE products SET name = ?,category = ?,price = ?,stock = ?,photo = ?WHERE id = ?',
            (name,category,price,stock,filename,id))
        conn.commit()
        conn.close()

        flash(f'{name} updated successfully!',"success")
        return redirect(url_for('product'))

    product = conn.execute('SELECT * FROM products WHERE id = ?',(id,)).fetchone()
    conn.close()

    if product is None: abort(404)
    return render_template("edit_product.html",product=product)

@app.route("/search")
def search():
    q = request.args.get('q', '')
    conn = get_db()

    if q:
        products = conn.execute(' SELECT * FROM products WHERE name LIKE ? OR category LIKE ? OR price LIKE ? OR stock LIKE ?',
            ( f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%')).fetchall()

    else:
        products = conn.execute('SELECT * FROM products ORDER BY id DESC').fetchall()
    conn.close()

    return render_template( "search.html", products=products, query=q)

@app.route("/filter")
def filter_products():
    conn = get_db()

    category = request.args.get("category","")
    min_price = request.args.get("min_price","")
    max_price = request.args.get("max_price","")

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
    products = conn.execute(query,params).fetchall()
    categories = conn.execute("SELECT DISTINCT category FROM products").fetchall()
    conn.close()

    return render_template( "filter.html", products=products, categories=categories, selected_category=category, 
    min_price=min_price, max_price=max_price)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        conn = get_db()
        existing = conn.execute('SELECT * FROM users WHERE username = ?',(username,)).fetchone()
        if existing:
            flash('Username already exists!','danger')
            conn.close()

            return render_template('register.html')
        hashed = generate_password_hash(password)
        conn.execute('INSERT INTO users(username, password, role)VALUES (?, ?, ?)',(username,hashed,'product'))

        conn.commit()
        conn.close()

        flash('Registration successful! Please login.','success')
        return redirect(url_for('login'))
    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?',(username,)).fetchone()
        conn.close()

        if (user and check_password_hash(user['password'],password)):
            session['username'] = username
            session['role'] = user['role']

            flash(f'Welcome {username}!','success')
            return redirect(url_for('home'))

        else:
            flash('Invalid username or password','danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username',None)
    session.pop('role',None)
    flash('You have been logged out.','info')
    return redirect(url_for('home'))

@app.route('/categories')
def categories():
    conn = get_db()
    rows = conn.execute('''
        SELECT categories.name AS category_name,COUNT(products.id) AS product_count
        FROM categories
        LEFT JOIN products
        ON products.category = categories.name
        GROUP BY categories.name
        ORDER BY categories.name
        ''').fetchall()
    conn.close()
    return render_template('categories.html',rows=rows)

@app.route("/order", methods=["GET", "POST"])
def order():
    conn = get_db()
    products = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()

    # Home page ke Orders button se product_id receive hoga
    product_id_from_home = request.args.get("product_id")
    selected_product = None
    if product_id_from_home:
        selected_product = conn.execute("SELECT * FROM products WHERE id = ?",(product_id_from_home,)).fetchone()

    if request.method == "POST":
        product_id = request.form.get("product")
        try:
            quantity = int(request.form.get("quantity", 1))
        except (ValueError, TypeError):
            quantity = 1

        customer_name = request.form.get("customer_name","").strip()
        customer_phone = request.form.get("customer_phone","").strip()
        address = request.form.get("address","").strip()

        if not product_id:
            conn.close()
            flash("Please select a product.", "danger")
            return redirect(url_for("order"))

        if quantity < 1:
            conn.close()
            flash("Quantity must be at least 1.","danger")
            return redirect(url_for("order"))
                            
        if not customer_name:
            conn.close()
            flash("Please enter customer name.","danger")
            return redirect(url_for("order"))

        if not customer_phone:
            conn.close()
            flash("Please enter mobile number.","danger")
            return redirect(url_for("order"))

        if not address:
            conn.close()
            flash("Please enter address.","danger")
            return redirect(url_for("order"))

        product = conn.execute("SELECT * FROM products WHERE id = ?",(product_id,)).fetchone()

        if product is None:
            conn.close()
            flash("Selected product not found.","danger")
            return redirect(url_for("order"))

        product_name = product["name"]
        price = float(product["price"])
        total = price * quantity
        order_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        # ORDER DATABASE ME PERMANENTLY SAVE HOGA
        conn.execute("""INSERT INTO orders( product_name, price, quantity, total, customer_name, customer_phone, address, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            ( product_name, price, quantity, total, customer_name, customer_phone, address, order_date))

        conn.commit()
        conn.close()

        flash("Order placed successfully!","success")
        return redirect(url_for("order"))

    # DATABASE SE SAARE ORDERS LOAD HONGE
    orders = conn.execute(" SELECT * FROM orders ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("order.html", products=products, orders=orders, selected_product=selected_product)

@app.route("/delete_order/<int:order_id>",methods=["POST"])
def delete_order(order_id):
    if session.get('role') != 'admin':
        flash("Admins only! You do not have permission to delete orders.","danger")
        return redirect(url_for("order"))
    conn = get_db()
    conn.execute("DELETE FROM orders WHERE id = ?",(order_id,))

    conn.commit()
    conn.close()
    flash("Order deleted successfully!","success")
    return redirect(url_for("order"))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404
init_db()
init_db()
conn = get_db()
conn.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        total REAL NOT NULL,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        address TEXT NOT NULL,
        date TEXT NOT NULL
    )
""")

conn.commit()
conn.close()

if __name__ == "__main__":
    app.run(debug=True)