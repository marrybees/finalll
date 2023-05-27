from flask import Flask, redirect, url_for, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__== 'main':
    app.run(debug=True)