from http import client

from click import prompt
from dotenv import load_dotenv
from flask import Flask, abort, redirect, render_template, request, flash, session, url_for
from database import get_db, init_db # Importing the database connection function
from groq import Groq
import os
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current file
load_dotenv(os.path.join(BASE_DIR, '.env'))  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = 'My Secret Key' #Needed for flashing messages

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')  # Define the upload folder path
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the upload folder if it doesn't exist

def allowed_file(filename):
    #only allow certain file extensions
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    page = request.args.get('page', 1, type=int)
    per_page = 8
    offset = (page - 1) * per_page
    conn = get_db()
    #All products from database
    products = conn.execute('SELECT * FROM products ORDER BY id DESC LIMIT ? OFFSET ?', (per_page, offset)).fetchall()
    total = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    conn.close()
    total_pages = (total + per_page - 1) // per_page  # Calculate total pages
    return render_template("home.html", products=products, page=page, total_pages=total_pages)

@app.route("/products")
def product():
    page = request.args.get('page', 1, type=int)
    per_page = 8
    offset = (page - 1) * per_page
    conn = get_db()
    products = conn.execute('SELECT * FROM products ORDER BY id DESC LIMIT ? OFFSET ?', (per_page, offset)).fetchall()
    total = conn.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    conn.close()
    total_pages = (total + per_page - 1) // per_page  # Calculate total pages
    return render_template("products.html", products=products, page=page, total_pages=total_pages)

@app.route("/products/<int:id>/tip")
def get_ai_tip(id):
    conn = get_db()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?", (id,)
    ).fetchone()
    conn.close()

    if product is None:
        abort(404)

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
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    tip = response.choices[0].message.content

    return render_template("detail.html", product=product, tip=tip)


#DELETE - remove by ID
@app.route('/delete/<int:id>')
def delete_product(id):
    if session.get('role') != 'admin':
        flash("Admins only!  You do not have permission", "danger")
        return redirect(url_for('home'))
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
    if session.get('role') != 'admin':
        flash("Admins only!  You do not have permission", "danger")
        return redirect(url_for('home'))
    
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

        #ADD: handle photo upload
        file = request.files.get('photo')
        filename = 'default.png'  # Default photo
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        conn = get_db()
        conn.execute(''' INSERT INTO products 
                    (name, category, price, stock, photo) VALUES (?, ?, ?, ?, ?)''', 
                    (new_product["name"], new_product["category"], new_product["price"], new_product["stock"], filename))
       
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
    if session.get('role') != 'admin':
        flash("Admins only!  You do not have permission", "danger")
        return redirect(url_for('home'))
    conn = get_db()

    if request.method == 'POST':
        name = request.form['product_name']
        category = request.form['category']
        price = request.form['price']
        stock = request.form['stock']

        if not name:
            flash('Name cannot be empty','danger')
            return redirect(url_for('edit_product',id=id))

        #ADD: handle photo upload
        file = request.files.get('photo')
        filename = 'default.png'  # Default photo
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # UPDATE record
        conn.execute("""
            UPDATE products
            SET name = ?, category = ?, price = ?, stock = ?, photo = ?
            WHERE id = ?
        """, (name, category, price, stock, filename, id))

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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        conn = get_db()
        # Check if username already exists
        existing = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if existing:
            flash('Username already exists!', 'danger')
            conn.close()
            return render_template('register.html')
        
        hashed = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, hashed, 'product'))
        conn.commit()
        conn.close()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['role'] = user['role']
            flash(f'Welcome {username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/categories')
def categories():
    conn = get_db()

    rows = conn.execute('''
        SELECT categories.name AS category_name, COUNT(products.id) AS product_count
        FROM categories
        LEFT JOIN products ON products.category = categories.name
        GROUP BY categories.name
        ORDER BY categories.name
    ''').fetchall()

    conn.close()
    return render_template('categories.html', rows=rows)

@app.route('/orders')
def orders():
    conn = get_db()
    orders = conn.execute('SELECT * FROM orders ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('orders.html', orders=orders)
       
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

init_db()  # Initialize the database

if __name__ == "__main__":
    app.run(debug=True)