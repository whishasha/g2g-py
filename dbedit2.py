import sqlite3

test_data = [ #tuteeID, tutorID, subject, classdate, classtime, classnotes
        ('2', '1', 'Maths', '2025-04-01', '15:00:00', 'Yup' ),
        ('2', '1', 'English', '2025-04-19', '15:00:00', 'Surprise!' ),
        ('2', '1', 'Maths', '2025-04-15', '23:00:00', 'Lorem ipsum dolor set booey shooey bam bomo' ),
        ('2', '1', 'English', '2025-04-02', '19:00:00', 'This, I will enjoy' ),
        ('2', '1', 'English', '2025-04-01', '14:02:00', 'I will survive!' ),
        ('3', '1', 'Maths', '2025-03-05', '15:30:00', 'A man who thinks about everything thinks about nothing at all...' ),
        ('2', '1', 'Maths', '2025-04-21', '15:00:00', 'Whoowheee!' )
        ]

from collections import defaultdict #this function is altered to fit the testData database structure
from json import dumps
events_data = defaultdict(lambda: defaultdict(list))
for event in test_data:
    subject = event[2]
    date = event[3]
    time = event[4]
    note = event[5]
    year_month = str(date[:7]) #isolates YYYY-MM [7 char long]
    day = int(date[8:10])

    classtime = time[:5]

    events_data[year_month][day].append({
        "time": time,
        "description": note,
        "subject": subject
    }) 
print(dumps(events_data, indent=3))

def executeit():
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # the below statement will either overrwrite class dates or add a new class date
    cur.executemany('''INSERT OR REPLACE INTO testDates(tuteeID, tutorID, subject, classdate, classtime, classnotes)
                VALUES(?, ?, ?, ?, ?, ?)''', test_data)
    con.commit()

    cur.close()
    con.close()
    print('Success!')
executeit()


