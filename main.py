from flask import Flask, render_template, request
from flask_bcrypt import Bcrypt

from waitress import serve

import sqlite3








app = Flask(__name__)
bcrypt = Bcrypt(app)


@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/login", methods = ['GET', 'POST'])
def login():
    print('User is accessing login page...')
    if request.method == "POST":
        name = request.form.get('name')
        password = request.form.get('password')
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        userRecord = cur.execute('''SELECT name, password FROM users WHERE name=?''', (name,)).fetchone()
        cur.close()
        con.close()

        print(bcrypt.check_password_hash(userRecord[1], password))

    return render_template('login.html')

@app.route("/inquire")
def inquire():
    return render_template('inquire.html')

# @app.route("/test")
# def test():
#     return render_template('renamethis.html')

@app.route("/user/home")
def user_home():
    return render_template('user_home.html')

@app.route("/user/timetable")
def user_timetable():
    return render_template('user_timetable.html')

@app.route("/user/account")
def user_account():
    return render_template('user_account.html')

mode = "dev"
if mode == "prod":
    serve(app, port=10000)
elif mode == "dev":
    app.run(host="0.0.0.0", port=10000, debug=True) 
