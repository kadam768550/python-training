from flask import Flask

app = Flask(__name__)

products = [
    {"id": 1, "name": "Laptop", "price": 50000},
    {"id": 2, "name": "Smartphone", "price": 20000},
    {"id": 3, "name": "Keyboard", "price": 1000},
    {"id": 4, "name": "Mouse", "price": 500}
]

@app.route('/')
def home():
    html = "<h1>Shop Inventory System</h1>"

    for product in products:
        html += f"<li>{product['name']} - {product['price']}</li>"

    return html

if __name__ == "__main__":
    app.run(debug=True)

