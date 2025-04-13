from flask import Flask, render_template, request, redirect, flash, url_for, send_file
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from waitress import serve
from uuid import uuid4
import os
import sqlite3
from dotenv import load_dotenv, find_dotenv
from werkzeug.utils import secure_filename
load_dotenv(find_dotenv())
encoded_secret_key = os.getenv("SECRET_KEY")

class User(UserMixin):
    pass

def make_unique(string): # for making a unique filepath to prevent clashing
    ident = uuid4().__str__()
    return f"{ident}-{string}" #combines the strings together

login_manager = LoginManager()
#John, banana

app = Flask(__name__)
login_manager.init_app(app)
bcrypt = Bcrypt(app)
app.config["SECRET_KEY"] = encoded_secret_key

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/test")
def test():
    return render_template('test_user_home.html')

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
        print(request.form)
        if 'register' in request.form:
            print('Processing registration')
            register()
    return render_template('user_account.html')

def register():
        print('hello')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        
        username = request.form.get('username')
        password = request.form.get('password')

        is_tutor = request.form.get('is_tutor')
        if is_tutor:
            is_tutor = 1
        else:
            is_tutor = 0

        encryptedpassword = bcrypt.generate_password_hash(password)
        
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        userRecord = cur.execute('''SELECT name FROM users WHERE name=?''', (username,)).fetchone()
        print(userRecord)
        if userRecord:
            print(f"Error: Account with {username} already exists")
        else:
            cur.execute('''INSERT INTO users(name, firstname, lastname, password, is_tutor) 
                        VALUES(?, ?, ?, ?, ?)''', 
                        (username, firstname, lastname, encryptedpassword, is_tutor))
            con.commit()
            print("Yeah you good")



        cur.close()
        con.close()

        return redirect("/")

# Beginning of file upload part


app.config['UPLOAD_FOLDER'] = 'files'
ALLOWED_EXTENSIONS = {'pdf'} #allowed file extensions
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000 #16MB max upload

def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
# Application example uses this feature called 'flash' will seems to be useful for sending messages to users.
@app.route("/upload", methods = ["GET", "POST"])
def file_upload():
    if request.method == "POST":
                # check if the post request has the file part
        print('POST received!')
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) #prevents malicious file changes by validating the filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) 
            file.save(filepath)
            print('Saved!')
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            cur.execute('''INSERT INTO files(name, filepath) VALUES(?, ?)''', (filename, filepath))
            

            con.commit()
            cur.close()
            con.close()

            return redirect(url_for('download_file', name=filename)) #
        
    return render_template('FileUpload.html')

@app.route('/<name>')
def download_file(name):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], name)
    return send_file(filepath)
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

