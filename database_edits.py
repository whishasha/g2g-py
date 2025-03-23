import sqlite3

con = sqlite3.connect('database.db')
cur = con.cursor()

cur.execute('''DROP TABLE users''')
cur.execute('''CREATE TABLE users(name varchar(50), password, firstname, lastname)''')

cur.close()
con.close()