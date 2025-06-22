#Includes all functions used in the backend which do not contribute directly to linking pages via the decorator
import sqlite3
from collections import defaultdict #this function is altered to fit the testData database structure
from json import dumps
from datetime import datetime


def is_valid_time(time_string, format):
    try:
        datetime.strptime(time_string, format)
        return True
    except ValueError:
        return False

def check_password_strength(password):
    message = ''
    if password is not None:
        if len(password) > 8 or len(password) < 128:
            if any(letter.isalpha() for letter in password):
                if any(letter.isnumeric() for letter in password):
                    if not password.isalnum(): # checks for existence of special characters
                        if any(letter.isupper() for letter in password):
                            message = 'Password is valid'
                            return (True, message)
                        else:
                            message = 'Password must contain at least 1 uppercase character'
                            return (False, message)
                    else:
                        message = 'Password must contain a special character'
                        return (False, message)
                else:
                    message = 'Password must contain at least 1 number'
                    return (False, message)
            else:
                message = 'Password must contain at least 1 character'
                return (False, message)
        else:
            message = 'Password out of bounds, please keep between 8 and 128 characters incl.'
            return (False, message)
    else:
        message = 'Please enter a password'
        return (False, message)

def new_assignment_ID():



    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # retrieves a list of all unique assignment IDs from the database
    assignmentIDs = cur.execute('''SELECT DISTINCT assignmentID FROM Assignments''').fetchall()

    formattedIDs = []
    for _ in assignmentIDs:
        formattedIDs.append(_[0])  


    # creates a newID 1 greater than the last assignmentID
    if formattedIDs:
        newID = max(formattedIDs) + 1
    else:
        newID = 1

    return newID

def set_assignment_files(assignmentID: int, status: int, filename: str, filepath: str):

    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('''INSERT INTO Files(assignmentID, status, name, filepath) VALUES(?, ?, ?, ?)''',
                (assignmentID, status, filename, filepath))
    
    con.commit()

    cur.close()
    con.close()

def set_assignment_details(assignmentID: int, tuteeID: int, tutorID: int, title: str, duedate:str, subject:str):
        if subject == "English" or subject == "Maths":
            con = sqlite3.connect('database.db')
            cur = con.cursor()



            cur.execute('''INSERT INTO Assignments(assignmentID, tuteeID, tutorID, title, duedate, is_completed, is_late, grade, subject) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (assignmentID, tuteeID, tutorID, title, duedate, False, None, None, subject))
            
            con.commit()
            cur.close()
            con.close()

def get_assignment_details(ID):
    assignments = defaultdict(list)

    con = sqlite3.connect('database.db')
    cur = con.cursor()

    assignmentDetails = cur.execute('''SELECT * FROM Assignments WHERE tuteeID=? OR tutorID=?''', (ID, ID)).fetchall()

    assignmentIDList = []

    for assignment in assignmentDetails:
        assignmentID = assignment[0]

        setAssignmentFilepaths = cur.execute('''SELECT name, filepath FROM Files WHERE assignmentID=? AND status=0''', (assignmentID,)).fetchall()
        formattedSetFilepaths = []
        formattedSetFilenames = []
        for _ in setAssignmentFilepaths:
            formattedSetFilepaths.append(_[1])
            formattedSetFilenames.append(_[0])

        submittedAssignmentFilepaths = cur.execute('''SELECT name, filepath FROM Files WHERE assignmentID=? AND status=1''', (assignmentID,)).fetchall()
        formattedSubmittedFilepaths = []
        formattedSubmittedFilenames = []
        for _ in submittedAssignmentFilepaths:
            formattedSubmittedFilepaths.append(_[1])
            formattedSubmittedFilenames.append(_[0])

        markedAssignmentFilepaths = cur.execute('''SELECT name, filepath FROM Files WHERE assignmentID=? AND status=2''', (assignmentID,)).fetchall()
        formattedMarkedFilepaths = []
        formattedMarkedFilenames = []
        for _ in markedAssignmentFilepaths:
            formattedMarkedFilepaths.append(_[1])
            formattedMarkedFilenames.append(_[0])

        newcon = sqlite3.connect('database.db')
        newcur = newcon.cursor()


        newcur.execute('''SELECT name FROM users WHERE ID = ?''', (assignment[1],))
        row = newcur.fetchone()

        newcon.close()


        assignments[assignmentID].append({
            "assignmentID": assignment[0],
            "tuteeID": assignment[1],
            "tutee": row[0],
            "tutorID": assignment[2],
            "title": assignment[3],
            "duedate": assignment[4],
            "is_completed": assignment[5],
            "is_late": assignment[6],
            "grade": assignment[7],
            "subject": assignment[8],
            "set_files": formattedSetFilepaths, # the initial assignment files w/ status 0
            "set_files_names": formattedSetFilenames,
            "submitted_files": formattedSetFilepaths,
            "submitted_files_names": formattedSetFilenames,
            "marked_files": formattedMarkedFilepaths,
            "marked_files_names": formattedMarkedFilenames 
        })
    cur.close()
    con.close()

    return assignments

def update_assignment_status(assignmentID: int, is_completed: int, grade: int):

    con = sqlite3.connect('database.db')
    cur = con.cursor()


    if is_completed == 0:
        cur.execute('''UPDATE Assignments SET is_completed = 0 WHERE assignmentID = ?''', (assignmentID,))
    if is_completed == 1:
        duedate = cur.execute('''SELECT duedate FROM Assignments WHERE assignmentID = ?''', (assignmentID,)).fetchone()[0]
        is_late = 0
        date = datetime.today().strftime('%Y-%m-%d')
        if duedate > date:
            is_late = 0
        elif duedate < date:
            is_late = 1

        cur.execute('''UPDATE Assignments SET is_completed = ?, is_late=?, grade=? WHERE assignmentID = ?''', (is_completed, is_late, grade, assignmentID,))
    con.commit()
    
    
    cur.close()
    con.close()

def get_tutees():

    con = sqlite3.connect('database.db')
    cur = con.cursor()

    tutees = cur.execute('''SELECT ID, firstname, lastname, name FROM users WHERE is_tutor=0''').fetchall()

    cur.close()
    con.close()

    formattedTutees = []
    for tutee in tutees:
        tuteeID = tutee[0]

        tuteeName = tutee[3]

        tuteeFullName = " ".join([str(tutee[1]), str(tutee[2])])

        formattedTutees.append((tuteeID, tuteeFullName, tuteeName))


    #Hopefully sorts the record by alphabetical order
    sorted(formattedTutees, key=lambda tutee: tutee[1].lower())


    return formattedTutees

def validate_file_access(unique_filename, userID):
    
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    assignmentID = cur.execute('''SELECT assignmentID from Files WHERE filepath=?''', (fr'static/files\{unique_filename}',)).fetchone()
    assignmentName = cur.execute('''SELECT name from Files WHERE filepath=?''', (fr'static/files\{unique_filename}',)).fetchone()
    
    if assignmentID is not None and assignmentName is not None:
        row = cur.execute('''SELECT tuteeID FROM Assignments WHERE assignmentID=?''', (assignmentID)).fetchone()[0]
        row1 = cur.execute('''SELECT tutorID FROM Assignments WHERE assignmentID=?''', (assignmentID)).fetchone()[0]
        
        
        if row == userID or row1 == userID:
            return assignmentName[0]
    


    cur.close()
    con.close()


    return False


def get_home_details(tuteeID):

    # show # of due assignments
    # show duedate, title of due assignment, subject in scrollable div

    # show enrolled classes
    # show upcoming classes => date, subject, classtime

    currentYearMonthDate = datetime.today().strftime('%Y-%m-%d')
    
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    
    # fetching assignment:
        # number of due assignments
        # duedate, title, subject
    assignment_details = cur.execute('''SELECT duedate, title, subject FROM Assignments WHERE tuteeID=? OR tutorID=? AND duedate > ? AND is_completed = 0''', (tuteeID, tuteeID, currentYearMonthDate)).fetchall()


    # fetching enrolled classes:
        # enrolled classes
    enrolled_classes = cur.execute('''SELECT is_english, is_maths FROM Classes WHERE userID=?''', (tuteeID,)).fetchone()

    # fetching class details:
        # upcoming classes where:
            # date > currentdate, subject, classtime
    class_times = cur.execute('''SELECT classdate, subject, classtime, title FROM Dates WHERE tuteeID=? OR tutorID=? AND classdate > ?''', (tuteeID, tuteeID, currentYearMonthDate)).fetchall()

    cur.close()
    con.close()

    return (assignment_details, enrolled_classes, class_times)

def unenroll_tutee(tuteeID):
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    #Validate that the tuteeID refers to an actual tutee
    validateTutee = cur.execute('''SELECT ID FROM users WHERE ID=?''', (tuteeID)).fetchone()

    if validateTutee is not None:
        validateTutee = validateTutee[0]
        try:
            cur.execute('''DELETE FROM users WHERE ID=?''', (tuteeID))
            
            assignmentIDs = cur.execute('''SELECT assignmentID FROM Assignments WHERE tuteeID=?''', (tuteeID)).fetchall()
            for assignmentID in assignmentIDs:
                cur.execute('''DELETE FROM Files WHERE assignmentID=?''', (assignmentID))

            cur.execute('''DELETE FROM Assignments WHERE tuteeID=?''', (tuteeID))
            cur.execute('''DELETE FROM Classes WHERE userID=?''', (tuteeID))
            con.commit()
            print('Successful deletion!')
            return True
        except:
            print('An error has occurred')

    cur.close()
    con.close()
    return False


if __name__ == '__main__':
    print('Running functions.py on main thread!')