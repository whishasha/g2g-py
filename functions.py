#Includes all functions used in the backend which do not contribute directly to linking pages via the decorator
import sqlite3


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