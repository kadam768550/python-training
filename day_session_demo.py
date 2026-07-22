import secrets
from flask import Flask, render_template, request, redirect, url_for, session, url_for, flash

app = Flask(__name__, template_folder='day_session_templates', static_folder='static')
app.secret_key = secrets.token_hex(16)  # Generate a random secret key for session management

@app.route('/')
def home():
    name = session.get('name')
    return render_template('home.html', name=name)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name  = request.form['name'.strip()]
        
        if not name:
            flash('Name is required!', 'danger')
            return render_template('register.html')
        
        session['name'] = name
        flash(f'Welcome, {name}!', 'success')
        return redirect(url_for('home'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('name', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)