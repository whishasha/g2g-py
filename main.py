from flask import Flask, render_template, request, session, redirect, flash, url_for, send_file, send_from_directory
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
from datetime import datetime
from html import escape

import shutil
#chat tutorial:
# https://www.youtube.com/watch%3Fv%3Do5vDco6OVTs&ved=2ahUKEwjswL677tiNAxUMT2wGHalHCcEQz40FegQIFxAr&usg=AOvVaw3gLy0_lglbLC22aR5czqpp

#----------------------------------------MISCELLANEOUS SECTION---------------------------------------------#
load_dotenv(find_dotenv())
encoded_secret_key = os.getenv("SECRET_KEY") or os.urandom(24)

# see Documentation for Flask_Login here:
# https://flask-login.readthedocs.io/en/latest/

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

    real_data = cur.execute('''SELECT * FROM Dates WHERE tutorID =? OR tuteeID =?''', (int(ID), int(ID))).fetchall()
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
            if day[0] == '0':
                day = day[1]
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


    return events_data

allowed_subjects = ['english', 'maths']



#----------------------------------------INITIALISATION SECTION---------------------------------------------#


login_manager = LoginManager()

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
    session.pop('_flashes', None)
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
        if userRecord is None:
            flash('Invalid username')
            flash('Please try again')
            return redirect(request.url)
        if userRecord:
            passwordValidated = bcrypt.check_password_hash(userRecord[2], password)
            if passwordValidated:
                #userRecord[0] = ID, [1] = username, [2] = encrypted password, [3] = is_tutor as a 1(TRUE) or 0 (FALSE)
                userID = str(userRecord[0])
                user = User(userID, userRecord[1], userRecord[2], userRecord[3])
                login_user(user) #from Flask_Login
                return redirect(url_for('user_home')) #add username as a parameter
            else: 
                flash('Invalid password')
                flash('Please try again')
                return redirect(request.url)
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
                    flash('Invalid information in form')
                    return redirect(request.url)
                else:
                    try:
                        tutee = str(request.form['tutee'])
                        classdate = str(request.form['classdate'])
                        classtime = str(request.form['classtimebegin'])
                        title = str(request.form['title'])
                        classnotes = str(request.form['classnotes'])
                        subject = str(request.form['subject'])     
                        escape(title)
                        escape(classnotes)
                    except:
                        flash('Invalid request')
                        return redirect(request.url)
                    
                    try:
                        tutee = int(tutee)
                    except:
                        flash('Invalid ID submitted')
                        return redirect(request.url)

                    # check for length of title, then restrict length
                    if len(title) > 100:
                        flash('Title too long. Restricted to 100 characters')
                        return redirect(request.url)

                    if len(classnotes) > 250:
                        flash('Notes too long. Restricted to 250 characters')
                        return redirect(request.url)

                    if subject not in allowed_subjects:
                        flash('Error. Please contact system administrator')
                        return redirect(request.url)

                    con = sqlite3.connect('database.db')
                    cur = con.cursor()


                    if not functions.is_valid_time(classtime, "%H:%M") or not functions.is_valid_time(classdate, "%Y-%m-%d"):
                        flash('Invalid date and time')
                        return redirect(request.url)

                    # details = cur.execute('''SELECT classdate, classtime FROM Dates WHERE tutorID=?''', (str(current_user.id))).fetchall()
                    details = cur.execute('''SELECT classdate, classtime FROM Dates WHERE tutorID=? AND classdate=? AND classtime=?''', (current_user.id, classdate, classtime)).fetchall()
                    if details:
                        flash('Date and time already in use. Please choose another.')
                        return redirect(request.url)                





                    cur.execute('''INSERT INTO Dates(tuteeID, tutorID, subject, classdate, classtime, classnotes, title) VALUES(?, ?, ?, ?, ?, ?, ?)''',
                                (tutee, current_user.id, subject, classdate, classtime, classnotes, title))
                    con.commit()

                    cur.close()
                    con.close()
                    flash('Class successfully set!')
            if 'change' in request.form:    #tutor-only function

                if 'class' not in request.form or 'classdate' not in request.form or 'classtimebegin' not in request.form or 'title' not in request.form or 'subject' not in request.form or 'classnotes' not in request.form:
                    flash('Invalid information in form')
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
                                    


                if len(title) > 100:
                    flash('Title too long. Restricted to 100 characters')
                    redirect(request.url)

                # get classID, then see if it exists. 
                # if exists:
                #   update the record with new information
                # alter calendar dates to hold ID as data
                con = sqlite3.connect('database.db')
                cur = con.cursor()
                # verify that class date exists for updating
                details = cur.execute('''SELECT classdate, classtime, tuteeID FROM Dates WHERE classdate=? AND classtime=? AND tutorID=? AND classID !=?''',(classdate, classtime, current_user.id, classID)).fetchone()

                if details:
                    flash('Invalid date to change. Class does not exist')
                    return redirect(request.url)

                # the below statement will either overrwrite class dates or add a new class date
                # cur.execute('''INSERT OR REPLACE INTO Dates(tuteeID, tutorID, subject, classdate, classtime, classnotes)
                #             VALUES(?, ?, ?, ?, ?, ?)''', formattedData)

                cur.execute('''UPDATE Dates SET subject=?, classdate=?, classtime=?, classnotes=?, title=? WHERE classID=?''',
                            (subject, classdate, classtime, classnotes, title, classID))

                con.commit()

                cur.close()
                con.close()
                flash('Class details updated')
            if 'delete' in request.form:
                    try:
                        classID = request.form.get('classID')
                        classID = int(classID)
                    except TypeError as e:
                        flash('Invalid request.')
                        return redirect(request.url)

                    con = sqlite3.connect('database.db')
                    cur = con.cursor()
                    
                    try:
                        cur.execute('''DELETE FROM Dates WHERE classID=?''', (classID,))
                        con.commit()
                    except:
                        print('Invalid SQL statement')
                        flash('An unexpected error has occurred.')
                        return redirect(request.url)
                    cur.close()
                    con.close()

                    flash('Successful deletion!')
    tutees = functions.get_tutees()
    
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    overview = cur.execute('''SELECT subject, classdate, classtime, title, classID FROM Dates WHERE tuteeID=? OR tutorID=? AND classdate >= ?''', (current_user.id, current_user.id, datetime.today().strftime('%Y-%m-%d'))).fetchall()

    return render_template('user_timetable.html', class_dates=init_real_data(current_user.id), tutees=tutees, overview=overview)


@app.route("/user/assignments", methods=['GET', 'POST'])
@login_required
def user_assignments():
    if request.method == "POST":
        if 'setassignment' in request.form:
            print('Setting assignment!')
            if not request.form['subject']:
                flash('No subject selected')
                return redirect(request.url)
            subject = request.form['subject']
            
            if subject.lower() not in allowed_subjects:
                flash('Invalid subject. Please try again.')
                return redirect(request.url)

            if not request.form['date']:
                flash('Invalid date')
                return redirect(request.url)
            duedate = str(request.form['date'])
            if not functions.is_valid_time(duedate, '%Y-%m-%d'):
                flash('Invalid time. Please try again')
                return redirect(request.url)

            tuteeID = request.form['tutee']
            if User.get(tuteeID) is None:
                flash('Invalid tutee ID!')
                return redirect(request.url)
            
            if User.get(tuteeID).is_tutor != 0:
                flash('Invalid tutee ID! Please contact system admin.')
                return redirect(request.url)                

            if not request.form['title']:
                flash('Title not set')
                return redirect(request.url)
            title = str(request.form['title'])
            escape(title)
            if len(title) > 250:
                flash('Title is too long.')
                return redirect(request.url)

            # If no file is uploaded, cancel request
            if 'file' not in request.files:
                flash('No file part(s) selected')
                return redirect(request.url)
            
            # request.files returns a MultiDict due to multiple files being uploaded
            # getlist('file') method returns a list of all values under the key 'list' from the dictionary
            # In this case we get FileStorage, which acts as an instance to store file data such as filename
            
            assignmentID = functions.new_assignment_ID()

            # code for uploading to the table handling assignment files
            for file in request.files.getlist('file'):
                if file.filename == '':
                    flash('No selected file')
                    return redirect(request.url)
                if file and allowed_file_pdf(file.filename):
                    filename = secure_filename(file.filename) #prevents malicious file changes by validating the filename
                    unique_filename = make_unique(filename) # https://stackoverflow.com/questions/61534027/how-should-i-handle-duplicate-filenames-when-uploading-a-file-with-flask
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename) 
                    file.save(filepath)
                    flash('Saved!')
                    functions.set_assignment_files(assignmentID, status=0, filename=filename, filepath=filepath)
                else:
                    flash('File limit is 25MB. Please try again.')
            flash('Assignment files set!')

            # after the files have been uploaded, we will now upload assignment details concerning the involved tutor, tutee, 
            # assignment, and name of the task
            functions.set_assignment_details(assignmentID=assignmentID, tuteeID=tuteeID, tutorID=current_user.id, title=title, duedate=duedate, subject=subject)
        if 'submitassignment' in request.form:
            if 'file' not in request.files:
                flash('No file selected')
                return redirect(request.url)
            
            if 'submitassignment' not in request.form:
                flash('Invalid request')
                return redirect(request.url)
            
            assignmentID = request.form['submitassignment']
            for file in request.files.getlist('file'):
                if file.filename == '':
                    flash('No selected files')
                    return redirect(request.url)
            
                if file and allowed_file_pdf(file.filename):
                    filename = secure_filename(file.filename) 
                    unique_filename = make_unique(filename) 
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename) 
                    file.save(filepath)
                    flash('Saved!')
                    functions.set_assignment_files(assignmentID=assignmentID, status=1, filename=unique_filename, filepath=filepath)
            # need to: upload files to Files, with status 1
            functions.update_assignment_status(assignmentID=assignmentID, is_completed=1, grade=None)
            # update Assignment, turning is_completed = 1
            
            flash('Assignment files submitted!')
        if 'unsubmitassignment' in request.form:
            assignmentID = request.form['unsubmitassignment']
            functions.update_assignment_status(assignmentID=assignmentID, is_completed=0, grade=None)
        if 'markassignment' in request.form:
            if 'file' not in request.files:
                flash('No file part(s) selected')
                return redirect(request.url)
            
            if 'grade' not in request.form:
                flash('No grade submitted!')
                return redirect(request.url)
            try:
                grade = int(request.form['grade'])
                if grade < 0 or grade > 100:
                    flash('Invalid grade entered!')
                    return redirect(request.url)
            except:
                flash('Invalid grade entered! Must be between 0 and 100')
                return redirect(request.url)
            
            assignmentID = request.form['markassignment']
            for file in request.files.getlist('file'):
                # if file.filename == '':
                #     flash('No selected file')
                #     return redirect(request.url)
            
                if file and allowed_file_pdf(file.filename):
                    filename = secure_filename(file.filename) 
                    unique_filename = make_unique(filename) 
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename) 
                    file.save(filepath)
                    flash('Saved!')
                    functions.set_assignment_files(assignmentID=assignmentID, status=2, filename=filename, filepath=filepath)
            # need to: upload files to Files, with status 2
            functions.update_assignment_status(assignmentID=assignmentID, is_completed=1, grade=grade)
            # update Assignment, turning is_completed = 1
            
            flash('Assignment marked & uploaded!!')
        if 'deleteassignment' in request.form:
            try:
                assignmentID = request.form['deleteassignment']
            except ValueError:
                flash('Invalid ID')
                return redirect(request.url)
            con = sqlite3.connect('database.db')
            cur = con.cursor()

            cur.execute('''DELETE FROM Assignments WHERE assignmentID=?''', (assignmentID,))
            cur.execute('''DELETE FROM Files WHERE assignmentID=?''', (assignmentID,))
            con.commit()
            
            cur.close()
            con.close()
            flash(f'Assignment with ID {assignmentID} successfully deleted!')
    assignments = functions.get_assignment_details(current_user.id) # returns all assignments associated with the user's ID
    tutees = functions.get_tutees()
    return render_template('user_assignments.html', assignments=assignments, tutees=tutees)


@app.route("/user/account", methods=["GET", "POST"])
@login_required
def user_account(): #A lot of the forms in here should be in their own "tutees" tab
    tutees=functions.get_tutees()
    if request.method == "POST":
        if 'register' in request.form:
            register()
        if 'registertutor' in request.form:
            register_tutor()
        if 'unenrolltutee' in request.form:
            if 'tutee' in request.form:
                try:
                    int(request.form['tutee'])
                except TypeError as e:
                    print(f'Attempted removal of invalid tutee | ID: {current_user.id}')
                    flash(f'Error: {e}')
                    redirect(request.url)
                except:
                    flash('Please contact system admin.')
                    redirect(request.url)
            tuteeID = request.form['tutee']
            if 'unenrollCheck' in request.form:
                if request.form['unenrollCheck'] == 'on':
                    if functions.unenroll_tutee(tuteeID):
                        flash('Succcess!')
                    else:
                        flash('Unsuccessful unenrolment')
            else:
                flash('Request denied')
                return redirect(request.url)
        if 'changepassword' in request.form:
            if 'password' in request.form:
                password = request.form['password']
                if 'confirmpassword' in request.form:
                    confirmpassword = request.form['confirmpassword']
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
                                flash('Success!')
                                return redirect(request.url)
                            else:
                                flash(strengthcheck[1])
                                return redirect(request.url)
                        else:
                            flash('Password cannot be the same as your previous password')
                            return redirect(request.url)
                        
            flash('Invalid request')
            return redirect(request.url)
        if 'changesubjects' in request.form:
            if 'tutee' in request.form:  
                if 'changeClassCheck' in request.form:
                    if request.form['changeClassCheck'] == 'on':
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

                                    cur.execute('''UPDATE Classes SET is_english = ?, is_maths = ? WHERE userID=? ''', (is_english, is_maths, tuteeID))
                                    con.commit()

                                    cur.close()
                                    con.close()
                                    flash('Success!')
                                else:
                                    flash('Invalid submission')
                                    return redirect(request.url)
                            else:
                                flash('Invalid request')
                                return redirect(request.url)
                        except:
                            flash('Invalid ID!')
                            return redirect(request.url)
                    else:
                        flash('Request cancelled')
                        return redirect(request.url)
            else:
                print(f'Suspicious class change form submission | ID: {current_user.id}') #Logging suspicious form submission
                flash('Invalid request')
                return redirect(request.url)


    return render_template('user_account.html', tutees=tutees)

def register():
        try:
            firstname = str(request.form.get('firstname'))
            lastname = str(request.form.get('lastname'))
            
            username = str(request.form.get('username'))
            password = str(request.form.get('password'))

            escape(firstname)
            escape(lastname)
            escape(username)
            escape(password)
            is_english = str(request.form.get('is_english'))
            is_maths = str(request.form.get('is_maths'))

            is_english = assign_int_boolean(is_english) #Turns str value of checkbox to boolean integer (1: True, 2: False)
            is_maths = assign_int_boolean(is_maths)
        except TypeError as e:
            flash('Error. Invalid fields submitted')
            return redirect(request.url)

        if not firstname: #input validation
            flash('Empty first name field!')
            return redirect(request.url)
        elif not lastname:
            flash('Empty last name field!')
            return redirect(request.url)
        elif not username:
            flash('Empty username')
            return redirect(request.url)
        elif not password:
            flash('Invalid password')
            return redirect(request.url)

        if len(firstname) > 250 or len(lastname) > 250 or len(username) > 250:
            flash('Fields cannot exceed 250 characters.')
            return redirect(request.url)

        #checking password strength
        passwordCheck = functions.check_password_strength(password=password)
        # returns a tuple, in which:
        # [0] = boolean value
        # [1] = error message

        if not passwordCheck[0]:
            return redirect(request.url)

        encryptedpassword = bcrypt.generate_password_hash(password).decode('utf-8')
        
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        usernameCheck = cur.execute('''SELECT name FROM users WHERE name=? AND firstname=? AND lastname=?''', (username, firstname, lastname)).fetchone()

        if cur.execute('''SELECT name FROM users WHERE name=?''', (username,)).fetchone():
            flash(f'Error: Account with username: {username} already exists.')

        if usernameCheck:
            flash(f"Error: Account with username: {username} and same name: {firstname} {lastname} already exists. Please enter a different username.")
        else:
            cur.execute('''INSERT INTO users(name, firstname, lastname, password, is_tutor) 
                        VALUES(?, ?, ?, ?, ?)''', 
                        (username, firstname, lastname, encryptedpassword, 0))
            con.commit()
            flash("Account registered!")

        registereduserID = cur.execute('''SELECT ID FROM users WHERE name=?''', (username,)).fetchone()
        if registereduserID: #checking if this has type None
            registereduserID = registereduserID[0]
        else:
            flash('An unexpected error has occurred') #user doesn't exist
            return redirect(request.url)
        
        cur.execute('''INSERT INTO Classes(userID, tutorID, is_english, is_maths) 
                    VALUES(?, ?, ?, ?)''',
                    (registereduserID, current_user.id, is_english, is_maths))
        con.commit()

        cur.close()
        con.close()

        return redirect("/")

def register_tutor():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    
    username = request.form.get('username')
    password = request.form.get('password')

    escape(firstname)
    escape(lastname)

    escape(username)
    escape(password)
    
    if not firstname: #input validation
        flash('Empty first name field!')
        return redirect(request.url)
    elif not lastname:
        flash('Empty last name field!')
        return redirect(request.url)
    elif not username:
        flash('Empty username')
        return redirect(request.url)
    elif not password:
        flash('Invalid password')
        return redirect(request.url)

    #checking password strength
    passwordCheck = functions.check_password_strength(password=password)
    # returns a tuple, in which:
    # [0] = boolean value
    # [1] = error message

    if not passwordCheck[0]:
        return redirect(request.url)

    encryptedpassword = bcrypt.generate_password_hash(password).decode('utf-8')
    
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    usernameCheck = cur.execute('''SELECT name FROM users WHERE name=?''', (username,)).fetchone()


    if usernameCheck:
        flash(f"Error: Account with {username} already exists")
    else:
        cur.execute('''INSERT INTO users(name, firstname, lastname, password, is_tutor) 
                    VALUES(?, ?, ?, ?, ?)''', 
                    (username, firstname, lastname, encryptedpassword, 1))
        con.commit()
        flash("Account registered!")

    registereduserID = cur.execute('''SELECT ID FROM users WHERE name=?''', (username,)).fetchone()

    if registereduserID: #checking if this has type None
        registereduserID = registereduserID[0]
    else:
        flash('An unexpected error has occurred') #user doesn't exist????!?!?!?!?!?
        return redirect(request.url)
    
    cur.close()
    con.close()

@login_required
@app.route("/user/notices", methods=['GET', 'POST'])
def user_notices():
    if request.method=='POST':
        if request.form:
            if 'create' in request.form:
                # NON-FILE INPUT VALIDATION
                if 'title' not in request.form or 'text' not in request.form or 'tag' not in request.form:
                    flash('Invalid request')
                try:
                    title = str(request.form.get('title'))
                    text = str(request.form.get('text'))
                    tag = int(request.form.get('tag'))
                except TypeError as e:
                    flash('Invalid fields submitted')
                if len(title) > 250:
                    flash('Title too long, please keep it below 250 characters')
                    return redirect(request.url)
                if not 0 <= tag <= 3:
                    flash('Invalid tag selected.')
                    return redirect(request.url)
                escape(title)
                escape(text) 

                date = datetime.today().strftime('%Y-%m-%d')
                poster = current_user.id
                con = sqlite3.connect('database.db')
                cur = con.cursor()
                
                check = cur.execute('''SELECT * FROM Notices WHERE title=? AND date=?''', (title, date)).fetchall()

                if check:
                    flash('Cannot have duplicate posts')
                    return redirect(request.url)


                cur.execute('''INSERT INTO Notices(title, text, tag, date, posterID) VALUES (?, ?, ?, ?, ?)''', (title, text, tag, date, poster))

                noticeID = cur.execute('''SELECT noticeID FROM Notices WHERE title=? AND text=? AND tag=? AND date=? AND posterID=?''',
                                    (title, text, tag, date, poster)).fetchone()[0]


                con.commit()


                #FILE-BASED INPUT VALIDATION
                if 'file' in request.files:
                    for file in request.files.getlist('file'):
                        if file:
                            fileroot = f'notices/{noticeID}'
                            if not os.path.exists(fileroot):
                                os.makedirs(fileroot)

                            if allowed_file_pdf(file.filename):
                                filename = secure_filename(file.filename) #prevents malicious file changes by validating the filename
                                unique_filename = make_unique(filename) # https://stackoverflow.com/questions/61534027/how-should-i-handle-duplicate-filenames-when-uploading-a-file-with-flask
                                filepath = os.path.join(fileroot, unique_filename) 
                                flash('Uploading!')
                                print(f'Uploading a PDF with filepath: {filepath} and \n filename: {filename}')
                                file.save(filepath)
                                cur.execute('''INSERT INTO NoticesFiles(noticeID, name, filepath) VALUES(?, ?, ?)''',
                                            (noticeID, filename, filepath))
                                con.commit()


                            if allowed_file_image(file.filename):
                                filename = secure_filename(file.filename) #prevents malicious file changes by validating the filename
                                unique_filename = make_unique(filename) # https://stackoverflow.com/questions/61534027/how-should-i-handle-duplicate-filenames-when-uploading-a-file-with-flask
                                filepath = os.path.join(fileroot, unique_filename) 
                                flash('Uploading image!')
                                print(f'Uploading an image with filepath: {filepath} and \n filename: {filename}')
                                file.save(filepath)
                                cur.execute('''UPDATE Notices SET imgfilepath=? WHERE noticeID=?''',
                                            (filepath, noticeID))
                                con.commit()
                            
                cur.close()
                con.close()

            if 'delete' in request.form:

                if current_user.id == 1:
                    try:
                        noticeID = request.form.get('noticeID')
                        noticeID = int(noticeID)
                    except e as TypeError:
                        flash('Invalid request.')
                        return redirect(request.url)

                    con = sqlite3.connect('database.db')
                    cur = con.cursor()
                    

                    # Creates and delete notice directories for storing files as needed

                    filedirectory = f'{app.config['UPLOAD_NOTICES']}/{noticeID}'
                    if os.path.exists(filedirectory):
                        shutil.rmtree(filedirectory)
                        # directory {filedirectory} has been deleted
                    else:
                        # directory {filedirectory} does not exist
                        pass
                    try:
                        cur.execute('''DELETE FROM Notices WHERE noticeID=?''', (noticeID,))
                        cur.execute('''DELETE FROM NoticesFiles WHERE noticeID=?''', (noticeID,))
                        con.commit()
                    except:
                        print('Invalid SQL statement')
                        flash('An unexpected error has occurred.')
                        return redirect(request.url)
                    cur.close()
                    con.close()

                    flash('Successful deletion!')


    con = sqlite3.connect('database.db')
    cur = con.cursor()

    notices = cur.execute('''SELECT * FROM Notices ORDER BY noticeID DESC''').fetchall()
    noticesfiles = cur.execute('''SELECT noticeID, name, filepath FROM NoticesFiles''').fetchall()
    from collections import defaultdict #this function is altered to fit the testData database structure
    from json import dumps
    notices_dict = defaultdict(list)
    for notice in notices:
        noticeID = str(notice[0])
        poster = User.get(str(notice[6])).username
        title = str(notice[1])
        text = str(notice[2])
        tag = str(notice[3])
        date = str(notice[5])
        imgfilepath = str(notice[4])

        if 'static' in imgfilepath[:6]:
            imgfilepath = imgfilepath[6:]


        attachments = []
        for attachment in noticesfiles:
            if int(attachment[0]) == int(noticeID):
                attachments.append(attachment)
        notices_dict[noticeID].append({
            "poster": poster,
            "title": title,
            "text": text,
            "tag": tag,
            "date": date,
            "img": imgfilepath,
            "attachments": attachments
        })

    return render_template("user_notices.html", notices=notices_dict)



@app.route("/user/logout")
@login_required
def logout():
    session.pop('_flashes', None)
    logout_user()
    return redirect("/")


# Beginning of file upload part

#----------------------------------------FILE UPLOAD SECTION---------------------------------------------#

app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['UPLOAD_NOTICES'] = 'static/notices'
ALLOWED_EXTENSIONS = {'pdf'} #allowed file extensions
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000 #16MB max upload

ALLOWED_IMAGES = {'jpeg', 'png', 'jpg'}

def allowed_file_pdf(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file_image(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGES


# https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
# Application example uses this feature called 'flash' will seems to be useful for sending messages to users.
@app.route("/upload", methods = ["GET", "POST"])
@login_required
def file_upload():
    if request.method == "POST":
                # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file_pdf(file.filename):
            filename = secure_filename(file.filename) #prevents malicious file changes by validating the filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) 
            file.save(filepath)
            flash('Saved!')
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            cur.execute('''INSERT INTO files(name, filepath) VALUES(?, ?)''', (filename, filepath))
            

            con.commit()
            cur.close()
            con.close()

            return redirect(url_for('download_file', name=filename))
        
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


mode = "prod"
if mode == "prod":
    try: 
     print('WGSI server running!')
     print('Please access the website on: http://127.0.0.1:10000/')
     serve(app, port=10000)
    except RuntimeError as e: 
        print(f'Error: {e}')
elif mode == "dev":
    print('Development server running!')
    app.run(host="127.0.0.1", port=10000, debug=True) 
# host="0.0.0.0"
# host="127.0.0.1"

