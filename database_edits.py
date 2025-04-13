import sqlite3

con = sqlite3.connect('database.db')
cur = con.cursor()

cur.execute('''DROP TABLE users''')
cur.execute('''CREATE TABLE users(ID INTEGER PRIMARY KEY   AUTOINCREMENT, name varchar(50), firstname, lastname, password, is_tutor BOOLEAN)''')
print('Success!')
cur.close()
con.close()