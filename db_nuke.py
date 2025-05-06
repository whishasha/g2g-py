import sqlite3

con = sqlite3.connect('database.db')
cur = con.cursor()

#cur.execute('''DROP TABLE users''')
#cur.execute('''CREATE TABLE users(ID INTEGER PRIMARY KEY   AUTOINCREMENT, name varchar(50), firstname, lastname, password, is_tutor BOOLEAN)''')

# cur.execute('''CREATE TABLE testClasses(userID, tutorID, is_english BOOL, is_maths BOOL)''')

cur.execute('''DROP TABLE testDates''')
cur.execute('''CREATE TABLE testDates(tuteeID, tutorID, subject TEXT, classdate DATE, classtime TIME, classnotes TEXT, title TEXT, classID INTEGER PRIMARY KEY, UNIQUE(classdate, classtime))''')


# cur.execute('''DROP TABLE testAssignments''')
# cur.execute('''CREATE TABLE testAssignments(assignmentID INTEGER PRIMARY KEY, tuteeID, tutorID, is_completed BOOLEAN, grade INTEGER)''')

# Q: What is status in testFiles?
# A: Status refers to the state of the assignment file:
# Is it:
# 0: The tutor's original assignment?
# 1: The tutee's uploaded files?
# 2: The tutor's returned files?

# if grade's value is NULL, then the assignment is not marked yet

cur.execute('''DROP TABLE testFiles''')
cur.execute('''CREATE TABLE testFiles(assignmentID INTEGER, status INTEGER, name, filepath, CONSTRAINT check_status CHECK(status BETWEEN -1 AND 3))''')


# this one really should be called AssignmentDetails

cur.execute('''DROP TABLE testAssignments''')
cur.execute('''CREATE TABLE testAssignments(assignmentID INTEGER PRIMARY KEY, tuteeID, tutorID, title, duedate DATE, is_completed BOOLEAN, is_late BOOLEAN, grade INTEGER, subject CONSTRAINT check_grade CHECK(grade BETWEEN -1 and 101))''')


print('Success!')
con.commit()

cur.close()
con.close()