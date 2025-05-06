from flask import Flask, render_template, request, redirect, flash, url_for, send_file, send_from_directory
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_wtf.csrf import CSRFProtect
from waitress import serve
from uuid import uuid4
import os
import sqlite3
from dotenv import load_dotenv, find_dotenv
from werkzeug.utils import secure_filename

import functions


#----------------------------------------MISCELLANEOUS SECTION---------------------------------------------#
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
        row = cur.execute('''SELECT ID, name, password, is_tutor FROM users WHERE name=?''', (username,)).fetchone()
        
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
def init_test_data(): #replace with dbedit2.py version
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
def init_real_data(ID): #fetches all events relevant to a user
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    real_data = cur.execute('''SELECT * FROM testDates WHERE tutorID =? OR tuteeID =?''', (int(ID), int(ID))).fetchall()
    cur.close()
    con.close()


    from collections import defaultdict #this function is altered to fit the testData database structure
    from json import dumps
    events_data = defaultdict(lambda: defaultdict(list))
    for event in real_data:
        if all(value is not None for value in event):
            subject = str(event[2])
            date = str(event[3])
            time = str(event[4])
            note = str(event[5])
            year_month = str(date[:7]) #isolates YYYY-MM [7 char long]
            day = str(date[8:10])
            id = int(event[7])
            title = str(event[6])
            classtime = str(time[:5])

            events_data[year_month][day].append({
                "time": classtime,
                "title": title,
                "description": note,
                "subject": subject,
                "id": id
            })

    print(dumps(events_data, indent=3))    #Hierarchy of events / debugging
    for event in events_data:
        print(event)
    return events_data




#----------------------------------------INITIALISATION SECTION---------------------------------------------#


login_manager = LoginManager()
# John, B@nan1aba => example tutor
# Alex, B@nan1aba => example tutee

#Initialising the application
app = Flask(__name__)

login_manager.init_app(app)
bcrypt = Bcrypt(app)


csrf = CSRFProtect(app)
csrf.init_app(app)

app.config["SECRET_KEY"] = encoded_secret_key


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

#----------------------------------------LANDING SECTION---------------------------------------------#

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


#----------------------------------------USER SECTION---------------------------------------------#
@app.route("/user/home")
@login_required
def user_home():
    #retrieves info to display on the homepage for tutees
    home_details = functions.get_home_details(current_user.id)
    return render_template('user_home.html', assignmentDetails = home_details[0], enrolledClasses = home_details[1], classDates = home_details[2])

@app.route("/user/timetable", methods=["GET","POST"])
@login_required
def user_timetable():
    if request.method == "POST": # for changing classdates => add verification for setting classes and changing classes

        if current_user.is_tutor == 1:
            if 'set' in request.form:  
                # Verifying user input
                if 'tutee' not in request.form or 'classdate' not in request.form or 'classtimebegin' not in request.form or 'title' not in request.form or 'subject' not in request.form or 'classnotes' not in request.form:
                    print('Invalid information in form')
                    return redirect(request.url)
                else:
                    try:
                        tutee = str(request.form['tutee'])
                        classdate = str(request.form['classdate'])
                        classtime = str(request.form['classtimebegin'])
                        title = str(request.form['title'])
                        classnotes = str(request.form['classnotes'])
                        subject = str(request.form['subject'])                 
                    except:
                        print('Invalid request')
                        return redirect(request.url)
                    
                    # check for length of title, then restrict length
                    if len(title) > 50:
                        print('Title too long. Restricted to 50 characters')
                        redirect(request.url)

                    con = sqlite3.connect('database.db')
                    cur = con.cursor()

                    # details = cur.execute('''SELECT classdate, classtime FROM testDates WHERE tutorID=?''', (str(current_user.id))).fetchall()
                    details = cur.execute('''SELECT classdate, classtime FROM testDates WHERE tutorID=? AND classdate=? AND classtime=?''', (current_user.id, classdate, classtime)).fetchall()
                    if details:
                        print('Date and time already in use. Please choose another.')
                        return redirect(request.url)                     
 # print(details)
#                    print(current_user.id)
                    # for record in details:
                    #     if record[0] == classdate: 
                    #         if record[1] == classtime:
                    #             print('Date and time already in use. Please choose another.')
                    #             return redirect(request.url) 

                    cur.execute('''INSERT INTO testDates(tuteeID, tutorID, subject, classdate, classtime, classnotes, title) VALUES(?, ?, ?, ?, ?, ?, ?)''',
                                (tutee, current_user.id, subject, classdate, classtime, classnotes, title))
                    con.commit()

                    cur.close()
                    con.close()
                    print('Assignment successfully set!')
            if 'change' in request.form:    #tutor-only function

                if 'class' not in request.form or 'classdate' not in request.form or 'classtimebegin' not in request.form or 'title' not in request.form or 'subject' not in request.form or 'classnotes' not in request.form:
                    print('Invalid information in form')
                    return redirect(request.url)
                else:
                    try:
                        classID = str(request.form['class'])
                        classdate = str(request.form['classdate'])
                        classtime = str(request.form['classtimebegin'])
                        title = str(request.form['title'])
                        classnotes = str(request.form['classnotes'])
                        subject = str(request.form['subject'])                  
                    except:
                        print('Invalid request')
                        return redirect(request.url)
                                    


                if len(title) > 50:
                    print('Title too long. Restricted to 50 characters')
                    redirect(request.url)

                # get classID, then see if it exists. 
                # if exists:
                #   update the record with new information
                # alter calendar dates to hold ID as data
                con = sqlite3.connect('database.db')
                cur = con.cursor()
                # verify that class date exists for updating
                details = cur.execute('''SELECT classdate, classtime, tuteeID FROM testDates WHERE classdate=? AND classtime=? AND tutorID=? AND classID !=?''',(classdate, classtime, current_user.id, classID)).fetchone()

                if details:
                    print('Invalid date to change. Class does not exist')
                    return redirect(request.url)

                # the below statement will either overrwrite class dates or add a new class date
                # cur.execute('''INSERT OR REPLACE INTO testDates(tuteeID, tutorID, subject, classdate, classtime, classnotes)
                #             VALUES(?, ?, ?, ?, ?, ?)''', formattedData)

                cur.execute('''UPDATE testDates SET subject=?, classdate=?, classtime=?, classnotes=?, title=? WHERE classID=?''',
                            (subject, classdate, classtime, classnotes, title, classID))

                con.commit()

                cur.close()
                con.close()
                print('Class details updated')

    print(current_user.id)
    tutees = functions.get_tutees()
    from json import dumps
    return render_template('user_timetable.html', class_dates=init_real_data(current_user.id), tutees=tutees)

def format_calendar_data(subject, tutee, daymonthyear, time, notes):
    #store daymonthyear in 2 separate variables:
    # DATE (YYYY-MM-DD)
    # TIME (HH:MM:SS)
    if current_user.is_tutor == 1:
        print('User is a tutor!')
        if User.find_by_username(tutee):
            tuteeID = User.find_by_username(tutee).id

            tutorID = current_user.id

            hours = str(time[0:2])
            minutes = str(time[3:5])
            seconds = '00'

            classTime = ":".join([hours, minutes, seconds]) #in form HH:MM:SS
            
            #will return a valid tuple which can be uploaded to the database
            return (tuteeID, tutorID, subject, daymonthyear, classTime, notes)
        else:
            print('User cannot be found.')
    print('Invalid request.')
    return None


@app.route("/user/assignments", methods=['GET', 'POST'])
@login_required
def user_assignments():
    if request.method == "POST":
        print(request.form)
        if 'setassignment' in request.form:

            if not request.form['subject']:
                print('No subject selected')
                return redirect(request.url)
            subject = request.form['subject']

            tuteeName = request.form['tutee']
            if not request.form['date']:
                print('Invalid date')
                return redirect(request.url)
            duedate = str(request.form['date'])

            if not request.form['tutee']:
                print('Invalid tutee') #change this to flash later
                return redirect(request.url)
            
            if not User.find_by_username(tuteeName):
                print('Invalid tutee')
                return redirect(request.url)

            if not request.form['title']:
                print('Title not set')
                return redirect(request.url)
            title = str(request.form['title'])

            # If no file is uploaded, cancel request
            if 'file' not in request.files:
                print('No file part(s) selected')
                return redirect(request.url)
            
            # request.files returns a MultiDict due to multiple files being uploaded
            # getlist('file') method returns a list of all values under the key 'list' from the dictionary
            # In this case we get FileStorage, which acts as an instance to store file data such as filename
            
            assignmentID = functions.new_assignment_ID()

            # code for uploading to the table handling assignment files
            for file in request.files.getlist('file'):
                if file.filename == '':
                    print('No selected file')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename) #prevents malicious file changes by validating the filename
                    unique_filename = make_unique(filename) # https://stackoverflow.com/questions/61534027/how-should-i-handle-duplicate-filenames-when-uploading-a-file-with-flask
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename) 
                    file.save(filepath)
                    print('Saved!')
                    functions.set_assignment_files(assignmentID, status=0, filename=filename, filepath=filepath)
            print('Assignment files set!')

            # after the files have been uploaded, we will now upload assignment details concerning the involved tutor, tutee, 
            # assignment, and name of the task
            tuteeID = User.find_by_username(tuteeName).id
            print(duedate)
            functions.set_assignment_details(assignmentID=assignmentID, tuteeID=tuteeID, tutorID=current_user.id, title=title, duedate=duedate, subject=subject)
        if 'submitassignment' in request.form:
            if 'file' not in request.files:
                print('No file part(s) selected')
                return redirect(request.url)
            
            if 'submitassignment' not in request.form:
                print('Invalid request')
                return redirect(request.url)
            
            assignmentID = request.form['submitassignment']
            for file in request.files.getlist('file'):
                if file.filename == '':
                    print('No selected file')
                    return redirect(request.url)
            
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename) 
                    unique_filename = make_unique(filename) 
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename) 
                    file.save(filepath)
                    print('Saved!')
                    functions.set_assignment_files(assignmentID=assignmentID, status=1, filename=unique_filename, filepath=filepath)
            # need to: upload files to testFiles, with status 1
            functions.update_assignment_status(assignmentID=assignmentID, is_completed=1, grade=None)
            # update testAssignment, turning is_completed = 1
            
            print('Assignment files submitted!')
        if 'unsubmitassignment' in request.form:
            print("It's going through!")
            assignmentID = request.form['unsubmitassignment']
            functions.update_assignment_status(assignmentID=assignmentID, is_completed=0, grade=None)
        if 'markassignment' in request.form:
            print(request.files)
            if 'file' not in request.files:
                print('No file part(s) selected')
                return redirect(request.url)
            
            if 'grade' not in request.form:
                print('No grade submitted!')
                return redirect(request.url)

            grade = int(request.form['grade'])
            assignmentID = request.form['markassignment']
            for file in request.files.getlist('file'):
                if file.filename == '':
                    print('No selected file')
                    return redirect(request.url)
            
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename) 
                    unique_filename = make_unique(filename) 
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename) 
                    file.save(filepath)
                    print('Saved!')
                    functions.set_assignment_files(assignmentID=assignmentID, status=2, filename=filename, filepath=filepath)
            # need to: upload files to testFiles, with status 2
            functions.update_assignment_status(assignmentID=assignmentID, is_completed=1, grade=grade)
            # update testAssignment, turning is_completed = 1
            
            print('Assignment marked & uploaded!!')
        if 'deleteassignment' in request.form:
            try:
                assignmentID = request.form['deleteassignment']
                print(assignmentID)
            except ValueError:
                print('Invalid ID')
                return redirect(request.url)
            con = sqlite3.connect('database.db')
            cur = con.cursor()

            cur.execute('''DELETE FROM testAssignments WHERE assignmentID=?''', (assignmentID,))
            cur.execute('''DELETE FROM testFiles WHERE assignmentID=?''', (assignmentID,))
            con.commit()
            
            cur.close()
            con.close()
            print(f'Assignment with ID {assignmentID} successfully deleted!')
    assignments = functions.get_assignment_details(current_user.id) # returns all assignments associated with the user's ID
    tutees = functions.get_tutees()
    
    return render_template('user_assignments.html', assignments=assignments, tutees=tutees)


@app.route("/user/account", methods=["GET", "POST"])
@login_required
def user_account(): #A lot of the forms in here should be in their own "tutees" tab
    tutees=functions.get_tutees()
    if request.method == "POST":
        print(request.form) #debug tool
        if 'register' in request.form:
            print('Processing registration')
            register()
        if 'unenrolltutee' in request.form:
            print('Unenrolling...')
            if 'tutee' in request.form:
                try:
                    int(request.form['tutee'])
                except TypeError as e:
                    print(f'Error: {e}')
                    redirect(request.url)
                except:
                    print('Other error')
                    redirect(request.url)
            tuteeID = request.form['tutee']
            if 'unenrollCheck' in request.form:
                if request.form['unenrollCheck'] == 'on':
                    if functions.unenroll_tutee(tuteeID):
                        print('Succcess!')
                    else:
                        print('Unsuccessful unenrolment')
            else:
                print('Request denied')
                return redirect(request.url)
        if 'changepassword' in request.form:
            print('Changing password...')
            if 'password' in request.form:
                password = request.form['password']
                print(password)
                if 'confirmpassword' in request.form:
                    confirmpassword = request.form['confirmpassword']
                    print(confirmpassword)
                    if password == confirmpassword:
                        passwordcheck = bcrypt.check_password_hash(current_user.password, password)
                        if not passwordcheck:
                            strengthcheck = functions.check_password_strength(password)
                            if strengthcheck[0]:
                                encryptedpassword = bcrypt.generate_password_hash(password).decode('utf-8')
                                con = sqlite3.connect('database.db')
                                cur = con.cursor()

                                cur.execute('''UPDATE users SET password = ? WHERE ID = ?''', (encryptedpassword, current_user.id))
                                con.commit()
                                cur.close()
                                con.close()
                                print('Success!')
                                return redirect(request.url)
                            else:
                                print(strengthcheck[1])
                        else:
                            print('Password cannot be the same as your previous password')
                        
            print('Invalid request')
            return redirect(request.url)
        if 'changesubjects' in request.form:
            if 'tutee' in request.form:  
                if 'unenrollCheck' in request.form:
                    if request.form['unenrollCheck'] == 'on':
                        try:
                            tuteeID = int(request.form['tutee'])
                            if any(int(tutee[0]) == tuteeID for tutee in tutees): #checks if the tutee is REAL
                                is_english = request.form.get('is_english')
                                is_maths = request.form.get('is_maths')

                                if is_english != None or is_english != 'on' or is_maths != None or is_maths != 'on': 
                                    is_english = assign_int_boolean(is_english)
                                    is_maths = assign_int_boolean(is_maths)

                                    con = sqlite3.connect('database.db')
                                    cur = con.cursor()

                                    cur.execute('''UPDATE testClasses SET is_english = ?, is_maths = ? WHERE userID=? ''', (is_english, is_maths, tuteeID))
                                    con.commit()

                                    cur.close()
                                    con.close()
                                    print('Success!')
                                else:
                                    print('Invalid submission')
                            else:
                                print('Invalid request')
                        except:
                            print('Invalid ID!')
                            return redirect(request.url)
                    else:
                        print('Request cancelled')
            else:
                print('Suspicious form submission')

    return render_template('user_account.html', tutees=tutees)

def register():
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


        #checking password strength
        passwordCheck = functions.check_password_strength(password=password)
        # returns a tuple, in which:
        # [0] = boolean value
        # [1] = error message

        if not passwordCheck[0]:
            print(passwordCheck[1])
            return redirect(request.url)

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

        registereduserID = cur.execute('''SELECT ID FROM users WHERE name=?''', (usernameCheck)).fetchone()
        if registereduserID: #checking if this has type None
            registereduserID = registereduserID[0]
        else:
            print('An unexpected error has occurred') #user doesn't exist????!?!?!?!?!?
            return redirect(request.url)
        if is_tutor == 0:
            cur.execute('''INSERT INTO testClasses(userID, tutorID, is_english, is_maths) 
                        VALUES(?, ?, ?, ?)''',
                        (registereduserID, current_user.id, is_english, is_maths))
            con.commit()

        cur.close()
        con.close()

        return redirect("/")

@app.route("/user/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


# Beginning of file upload part

#----------------------------------------FILE UPLOAD SECTION---------------------------------------------#

app.config['UPLOAD_FOLDER'] = 'static/files'
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

# @app.route('/<name>') #accessing files
# @login_required
# def download_file(name):
#     filepath = os.path.join(app.config['UPLOAD_FOLDER'], name)
#     return send_file(filepath)

@app.route('/static/files/<path:filename>')
@login_required
def get_link(filename):
    validated = functions.validate_file_access(filename, current_user.id)
    if validated: #returns as the name of filepath, not jumbled
        return send_from_directory(directory=app.config['UPLOAD_FOLDER'], path=filename)
    redirect("/")


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

