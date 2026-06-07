from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>My Shop</h1>'

@app.route('/about')
def about():
    return '<h1>About Us</h1><p>Shop inventory system</p>'

@app.route('/product')
def product():
    return '<h1>product</h1><p>product details</p>'


if __name__ == '__main__':
    app.run(debug=True)

    
