#Includes all functions used in the backend which do not contribute directly to linking pages via the decorator
import sqlite3
from collections import defaultdict #this function is altered to fit the testData database structure
from json import dumps
from datetime import datetime


def new_assignment_ID():



    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # retrieves a list of all unique assignment IDs from the database
    assignmentIDs = cur.execute('''SELECT DISTINCT assignmentID FROM testFiles''').fetchall()

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
    cur.execute('''INSERT INTO testFiles(assignmentID, status, name, filepath) VALUES(?, ?, ?, ?)''',
                (assignmentID, status, filename, filepath))
    
    con.commit()

    cur.close()
    con.close()

def set_assignment_details(assignmentID: int, tuteeID: int, tutorID: int, title: str, duedate:str, subject:str):
        if subject == "English" or subject == "Maths":
            con = sqlite3.connect('database.db')
            cur = con.cursor()



            cur.execute('''INSERT INTO testAssignments(assignmentID, tuteeID, tutorID, title, duedate, is_completed, is_late, grade, subject) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (assignmentID, tuteeID, tutorID, title, duedate, False, None, None, subject))
            
            con.commit()
            cur.close()
            con.close()

def get_assignment_details(ID):
    assignments = defaultdict(list)

    con = sqlite3.connect('database.db')
    cur = con.cursor()

    assignmentDetails = cur.execute('''SELECT * FROM testAssignments WHERE tuteeID=? OR tutorID=?''', (ID, ID)).fetchall()

    assignmentIDList = []

    for assignment in assignmentDetails:
        assignmentID = assignment[0]

        setAssignmentFilepaths = cur.execute('''SELECT name, filepath FROM testFiles WHERE assignmentID=? AND status=0''', (assignmentID,)).fetchall()
        formattedSetFilepaths = []
        formattedSetFilenames = []
        for _ in setAssignmentFilepaths:
            formattedSetFilepaths.append(_[1])
            formattedSetFilenames.append(_[0])

        submittedAssignmentFilepaths = cur.execute('''SELECT name, filepath FROM testFiles WHERE assignmentID=? AND status=1''', (assignmentID,)).fetchall()
        formattedSubmittedFilepaths = []
        formattedSubmittedFilenames = []
        for _ in submittedAssignmentFilepaths:
            formattedSubmittedFilepaths.append(_[1])
            formattedSubmittedFilenames.append(_[0])

        markedAssignmentFilepaths = cur.execute('''SELECT name, filepath FROM testFiles WHERE assignmentID=? AND status=2''', (assignmentID,)).fetchall()
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
        cur.execute('''UPDATE testAssignments SET is_completed = 0 WHERE assignmentID = ?''', (assignmentID,))
    if is_completed == 1:
        duedate = cur.execute('''SELECT duedate FROM testAssignments WHERE assignmentID=?''', (assignmentID,)).fetchone()[0]
        is_late = 0
        date = datetime.today().strftime('%Y-%m-%d')
        if duedate > date:
            is_late = 0
        elif duedate < date:
            is_late = 1

        cur.execute('''UPDATE testAssignments SET is_completed = ?, is_late=?, grade=? WHERE assignmentID = ?''', (is_completed, is_late, grade, assignmentID,))
    con.commit()
    
    
    cur.close()
    con.close()
    

if __name__ == '__main__':
    print('Running functions.py on main thread!')
    print(dumps(get_assignment_details(1), indent=2))