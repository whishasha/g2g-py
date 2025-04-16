from flask import Flask, render_template, request, redirect, flash, url_for, send_file
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from waitress import serve
from uuid import uuid4
import os
import sqlite3
from dotenv import load_dotenv, find_dotenv
from werkzeug.utils import secure_filename
load_dotenv(find_dotenv())
encoded_secret_key = os.getenv("SECRET_KEY")

# see Documentation for Flask_Login here:
# https://flask-login.readthedocs.io/en/latest/

# + Help from my friend ChatGPT!
class User(UserMixin):
    def __init__(self, id, username, password, is_tutor):
        self.id = id
        self.username = username
        self.password = password
        self.is_tutor = is_tutor #is assigned 1 (TRUE) or 0 (FALSE)

    @staticmethod
    def get(user_id):
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("SELECT ID, name, password, is_tutor FROM users WHERE ID = ?", (user_id,))
        row = cur.fetchone()
        con.close()
        if row:
            print(User(*row).username) #unpacks user tuple and returns a USER OBJECT
            return User(*row)
        return None

    @staticmethod
    def find_by_username(username):
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        row = cur.execute('''SELECT ID, name, password FROM users WHERE name=?''', (username,)).fetchone()
        
        cur.close()
        con.close()
        if row:
            return User(*row)
        return None
def make_unique(string): # for making a unique filepath to prevent clashing
    ident = uuid4().__str__()
    return f"{ident}-{string}" #combines the strings together

def assign_int_boolean(var):
    if var:
        var = 1 #True
    else:
        var = 0 #False
    return var

def init_test_data():
    from collections import defaultdict
    from json import dumps

    events = [
        ("Maths", "2025-04-01 15:00", "Meeting with John at 3 PM", "Pretty chill"),
        ("Philosophy", "2025-04-01 18:00", "Evening walk", "With my pal Carl Jung"),
        ("English", "2025-04-02 10:00", "Doctor's appointment at 10 AM", "Dreading it."),
        ("English", "2025-04-02 14:00", "Lunch with Sarah", ""),
        ("Astrophysics", "2025-05-01 00:00", "Holiday - May Day", "Time to kick back!"),
        ("Maths", "2025-05-02 11:00", "Meeting with client at 11 AM", "")
    ]

    events_data = defaultdict(lambda: defaultdict(list))


    for event in events:
        subject, datetime, description, notes = event #unpacks the tuple (dateTime = event[0], etc.)
        
        date, time = datetime.split(' ')
        year_month = str(date[:7]) #isolates YYYY-MM [7 char long]
        day = int(date[8:10])


        events_data[year_month][day].append({
            "time": time,
            "description": description,
            "subject": subject
        }) 
    return events_data

# print(dumps(events_data, indent=3))    Hierarchy of events



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


@app.route("/login", methods = ['GET', 'POST'])
def login():
    print('User is accessing login page...')
    if request.method == "POST":
        name = request.form.get('name')
        password = request.form.get('password')
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        userRecord = cur.execute('''SELECT ID, name, password, is_tutor FROM users WHERE name=?''', (name,)).fetchone()
        cur.close()
        con.close()
        passwordValidated = bcrypt.check_password_hash(userRecord[2], password)
        print(passwordValidated)
        if passwordValidated:
            #userRecord[0] = ID, [1] = username, [2] = encrypted password, [3] = is_tutor as a 1(TRUE) or 0 (FALSE)
            userID = str(userRecord[0])
            user = User(userID, userRecord[1], userRecord[2], userRecord[3])
            login_user(user) #from Flask_Login
            print('Successfully logged in')
            return redirect(url_for('user_home')) #add username as a parameter
    return render_template('login.html')

@app.route("/inquire")
def inquire():
    return render_template('inquire.html')


@app.route("/pricing")
def pricing():
    return render_template('pricing.html')

@app.route("/about")
def about():
    return render_template('about.html')



@app.route("/user/home")
@login_required
def user_home():
    return render_template('user_home.html')

@app.route("/user/timetable")
@login_required
def user_timetable():
    return render_template('user_timetable.html', class_dates=init_test_data())


@app.route("/user/assignments")
@login_required
def user_assignments():
    return render_template('user_assignments.html')

@app.route("/user/account", methods=["GET", "POST"])
@login_required
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

        is_english = request.form.get('is_english')
        is_maths = request.form.get('is_maths')
        is_tutor = request.form.get('is_tutor')

        is_english = assign_int_boolean(is_english) #Turns str value of checkbox to boolean integer (1: True, 2: False)
        is_maths = assign_int_boolean(is_maths)
        is_tutor = assign_int_boolean(is_tutor)

        print(f'{is_english} + {is_maths} + {is_tutor} + {current_user.is_tutor}')
        encryptedpassword = bcrypt.generate_password_hash(password).decode('utf-8')
        
        con = sqlite3.connect('database.db')
        cur = con.cursor()

        usernameCheck = cur.execute('''SELECT name FROM users WHERE name=?''', (username,)).fetchone()
        print(usernameCheck)


        if usernameCheck:
            print(f"Error: Account with {username} already exists")
        else:
            cur.execute('''INSERT INTO users(name, firstname, lastname, password, is_tutor) 
                        VALUES(?, ?, ?, ?, ?)''', 
                        (username, firstname, lastname, encryptedpassword, is_tutor))
            con.commit()
            print("Account registered!")

        registereduserID = cur.execute('''SELECT ID FROM users WHERE name=?''', (usernameCheck)).fetchone()[0]
        if is_tutor == 0:
            cur.execute('''INSERT INTO testClasses(userID, tutorID, is_english, is_maths) 
                        VALUES(?, ?, ?, ?)''',
                        (registereduserID, current_user.id, is_english, is_maths))
            con.commit()

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
@login_required
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
@login_required
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

