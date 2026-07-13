from flask import Flask, render_template, request, flash

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


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/products")
def product():
    return render_template("product.html", products=products)


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
        products.append(new_product)
        flash("Product added successfully!", "success")
        print("Updated Products List:", products)  # Debugging line to check the updated products list
        return render_template("product.html", products=products)

    return render_template("add_product.html")

if __name__ == "__main__":
    app.run(debug=True)