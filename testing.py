from collections import defaultdict
from json import dumps


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
    
print(events_data["2025-05"][1][0])