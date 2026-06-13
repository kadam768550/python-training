from flask import Flask, render_template

app = Flask(__name__)

prod = [
    {"name": "Laptop", "price": 50000, "stock": 10, "quality": "Good"},
    {"name": "Mouse", "price": 800, "stock": 50, "quality": "Average"},
    {"name": "Keyboard", "price": 1000, "stock": 30, "quality": "Good"},
    {"name": "Monitor", "price": 15000, "stock": 15, "quality": "Average"}
]

@app.route('/')
def home():
    return render_template('home.html')
 
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products')
def products():
    return render_template('products.html', products=prod)


if __name__ == '__main__':
    app.run(debug=True)