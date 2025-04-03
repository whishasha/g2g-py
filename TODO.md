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

[ ] add hover div for class details in calendar
    - if click on date, then
        - div appears over


[-] make website compatible with screen sizes using @media (see resources.md)

## Short-Term Tasks


[X] do smooth file up code for navbar in landing page

[] graphic design for landing pages

[] graphic designs for icons
