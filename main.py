from flask import Flask, render_template, request, redirect
from flask_bcrypt import Bcrypt

from waitress import serve

import sqlite3




# admin account:
# user0, hello

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

@app.route("/user/account", methods=["GET", "POST"])
def user_account():
    if request.method == "POST":
        if 'register' in request.form:
            register()
    return render_template('user_account.html')

def register():
        print('hello')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        
        username = request.form.get('username')
        password = request.form.get('password')

        encryptedpassword = bcrypt.generate_password_hash(password)
        
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        userRecord = cur.execute('''SELECT name FROM users WHERE name=?''', (username,)).fetchone()
        print(userRecord)
        if userRecord:
            print(f"Error: Account with {username} already exists")
        else:
            cur.execute('''INSERT INTO users(name, password, firstname, lastname) 
                        VALUES(?, ?, ?, ?)''', 
                        (username, encryptedpassword, firstname, lastname))
            con.commit()
            print("Yeah you good")



        cur.close()
        con.close()

        return redirect("/")




mode = "dev"
if mode == "prod":
    try: 
     print('WGSI server running!')
     serve(app, port=10000)
    except RuntimeError as e: 
        print(f'Error: {e}')
elif mode == "dev":
    print('Development server running!')
    app.run(host="127.0.0.1", port=10000, debug=True) 
# host="0.0.0.0"