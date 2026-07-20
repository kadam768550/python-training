from flask import Flask, render_template, request, flash

app = Flask(__name__)

app.secret_key = 'my secret key' # Needed for flashing messages

@app.route("/")
def home():
    return '<h1>My Project</h1>'


if __name__ == "__main__":
    app.run(debug=True)



