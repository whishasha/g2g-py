#Includes all functions used in the backend which do not contribute directly to linking pages via the decorator
import sqlite3
from collections import defaultdict #this function is altered to fit the testData database structure
from json import dumps

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

def set_assignment_details(assignmentID: int, tuteeID: int, tutorID: int, title: str, duedate:str):
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    cur.execute('''INSERT INTO testAssignments(assignmentID, tuteeID, tutorID, title, duedate, is_completed, grade) VALUES(?, ?, ?, ?, ?, ?, ?)''',
                (assignmentID, tuteeID, tutorID, title, duedate, False, None))
    
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

        assignmentFilepaths = cur.execute('''SELECT name, filepath FROM testFiles WHERE assignmentID=? AND status=0''', (assignmentID,)).fetchall()
        print(assignmentFilepaths)
        formattedFilepaths = []
        formattedFilenames = []
        for _ in assignmentFilepaths:
            formattedFilepaths.append(_[1])
            formattedFilenames.append(_[0])


        assignments[assignmentID].append({
            "assignmentID": assignment[0],
            "tuteeID": assignment[1],
            "tutorID": assignment[2],
            "title": assignment[3],
            "duedate": assignment[4],
            "is_completed": assignment[5],
            "grade": assignment[6],
            "set_files": formattedFilepaths, # the initial assignment files w/ status 0
            "set_files_names": formattedFilenames
        })
    cur.close()
    con.close()

    return assignments

print(dumps(get_assignment_details(1), indent=2))