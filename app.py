from flask import Flask, render_template

app = Flask(__name__)

prod = [
    {"name": "Laptop", "price": 50000, "quality": "Good"},
    {"name": "Mouse", "price": 1000, "quality": "Excellent"},
    {"name": "Keyboard", "price": 2000, "quality": "Average"},
    {"name": "Smartphone", "price": 30000, "quality": "Good"}
]

@app.route('/')
def home():
    return render_template('home.html',products=prod,latest_products=prod[:3])
@app.route('/sales')
def sales():
    return render_template('Sales.html')
@app.route('/suppliers')
def suppliers():
    return render_template('Suppliers.html')
@app.route('/products')
def product_list():
    return render_template('products.html',products=prod)

if __name__ == '__main__':
    app.run(debug=True)

