from flask import Flask, redirect, url_for, render_template, session, request, flash
from flask_sqlalchemy import SQLAlchemy
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'friut'



class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __str__(self):
        return f"your username:{self.username},password:{self.password}"

def scrape_crypto_data():
    url = 'https://finance.yahoo.com/crypto/'
    response = requests.get(url)
    content = response.content
    soup = BeautifulSoup(content, 'html.parser')

    table_body = soup.find('table').find('tbody')
    crypto_rows = table_body.find_all('tr')

    crypto_data = []
    for row in crypto_rows:
        name = row.find('td', {'aria-label': "Name"}).text
        price = row.find('td', {'aria-label': 'Price (Intraday)'}).text
        change = row.find('td', {'aria-label': 'Change'}).text
        percent_change = row.find('td', {'aria-label': '% Change'}).text
        market_cap = row.find('td', {'aria-label': 'Market Cap'}).text
        crypto_data.append([name, price, change, percent_change, market_cap])

    headers = ['Name', 'Price', 'Change', 'Percent Change', 'Market Cap']
    return crypto_data, headers

@app.route('/')
def home():
    crypto_data, headers = scrape_crypto_data()
    return render_template('home.html', crypto_data=crypto_data, headers=headers)


@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        new_user = Users(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route("/user")
def user():
    if 'username' in session:
        user = session['username']
        return render_template('user.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search_query']
        return render_template('search.html', search_query=search_query)

    return render_template('search.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username']= username

        user = Users.query.filter_by(username=username).first()
        if user and user.username == username and user.password == password:
            flash('Login successful!', 'success')
            return redirect(url_for('user'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop("username", None)
    return render_template('logout.html')

if __name__ == 'main':
    app.run(debug=True)


