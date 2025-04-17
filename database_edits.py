import sqlite3

con = sqlite3.connect('database.db')
cur = con.cursor()

#cur.execute('''DROP TABLE users''')
#cur.execute('''CREATE TABLE users(ID INTEGER PRIMARY KEY   AUTOINCREMENT, name varchar(50), firstname, lastname, password, is_tutor BOOLEAN)''')

# cur.execute('''CREATE TABLE testClasses(userID, tutorID, is_english BOOL, is_maths BOOL)''')

cur.execute('''DROP TABLE testDates''')
cur.execute('''CREATE TABLE testDates(tuteeID, tutorID, classdate DATE, classtime TIME, classnotes TEXT, UNIQUE(classdate, classtime))''')

print('Success!')
cur.close()
con.close()