import secrets
from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='day_session_templates')
app.secret_key = secrets.token_hex(16)

# Temporary — list mein store karenge memory mein
# Real project mein hum database use karenge (users table)
users = []
# Har user aisa dikhega: {'username': 'rahul', 'password': 'scrambled_text'}


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        # Step 1 — check karo username already hai ya nahi
        for user in users:
            if user['username'] == username:
                flash('Yeh username already liya gaya hai!', 'danger')
                return render_template('register.html')

        # Step 2 — password ko HASH karo, seedha store nahi karna
        hashed_password = generate_password_hash(password)
        # generate_password_hash — password ko scramble karta hai
        # original password kahin store nahi hota — sirf scrambled version

        # Step 3 — naya user list mein add karo
        users.append({
            'username': username,
            'password': hashed_password
        })

        flash('Register ho gaye! Ab login karo.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        # Step 1 — users list mein yeh username dhundo
        for user in users:
            if user['username'] == username:

                # Step 2 — password match karta hai?
                if check_password_hash(user['password'], password):
                    # check_password_hash — typed password ko bhi
                    # scramble karke compare karta hai stored scrambled version se
                    # match kare to True, nahi to False

                    session['username'] = username
                    # YEH WAHI LINE HAI JO KAL SEEKHI THI

                    flash(f'Welcome {username}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Password galat hai!', 'danger')
                    return render_template('login.html')

        # Yahan tak pahunche matlab username mila hi nahi
        flash('Yeh username register nahi hai!', 'danger')
        return render_template('login.html')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    # YEH HAI "PROTECTED PAGE" — sirf logged in log dekh sakte hain

    if 'username' not in session:
        # session mein 'username' hai hi nahi — matlab koi login nahi hai
        flash('Pehle login karo!', 'warning')
        return redirect(url_for('login'))

    return render_template('dashboard.html', username=session['username'])


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logout ho gaye!', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, port=5003)