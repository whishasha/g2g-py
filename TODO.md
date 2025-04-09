# Long-Term Tasks
 [] create database tables for sql
    - tutor: storing tutee names, primary key (tuteeID) username, password
    - tutee: storing tutee names, primary key (tutorID) username, password
    - preferences: colour scheme
    - classes: classes for each person, date/s, details => store as 00000 (place 1 if they are enrolled in that class)
    - assignments: (tuteeID, tutorID, BLOB)
    https://firebase.google.com/docs/database/admin/structure-data (helpful website)


[X] finish adding pages:
    - account (change pwd, email, request to change classes, contact tutee, change colour scheme)

[X] create login base functionality
    - do not forget to encrypt with python bcrypt

[] add password restrictions and prevent SQL injections
    - + account lockouts
    - linking to email for pwd recovery will be a later task

[-] add hover div for class details in calendar
    - if click on date, then
        - div appears over


[-] make website compatible with screen sizes using @media (see resources.md)

## Short-Term Tasks

**Functional**

[ ] add jinja to make the register tutee form only visible to tutors

[ ] add tutee registration

[ ] make it so you can add class details on calendar [for tutor], and request changes [for tutee] using jinja

[ ] add unique pages depending on username

[ ] add homework page

[ ] implement file uploads

**Non-Functional**

[X] do smooth file up code for navbar in landing page

[ ] format the nice dateInfo for the calendar

[ ] fix double scrollbar issue

[ ] graphic design for landing pages

[ ] graphic designs for icons
