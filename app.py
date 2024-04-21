from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, jsonify


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)

@app.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)


@app.route('/home')
def home():
    events = Event.query.all()
    return render_template('home.html', events=events)

@app.route('/add_event', methods=['POST'])
def add_event():
    name = request.form['name']
    date = request.form['date']

    new_event = Event(name=name, date=date)
    db.session.add(new_event)
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Choose a different username.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and password.', 'danger')

    return render_template('login.html')



@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Add authentication check here if needed
    return render_template('dashboard.html')


@app.route('/rasa', methods=['GET', 'POST'])
def forward_to_rasa():
    
    user_message = request.form['message']
    rasa_endpoint = 'http://localhost:5005/webhooks/rest/webhook'
    rasa_data = {'sender': 'user', 'message': user_message}

    rasa_response = requests.post(rasa_endpoint, json=rasa_data).json()
    return jsonify(rasa_response)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
