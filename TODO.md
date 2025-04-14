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

# UI DEISNG FIRST!! DO UI DEIGNS!! 
[ ] UI DEISNG
    [X] homework
    [ ] creating a user
    [ ] add CLASSES!
    [ ] fix the doodoo ugly form in user_account
    [X] cleanup + animations
    [ ] adding info about G2G
    [ ] remove login by Google bit from Login
    [ ] LINK PAGES!!!
    [X] remake logo

[X] login required thing

[X] add sessions

[ ] add jinja to make the register tutee form only visible to tutors

[X] add tutee registration

[ ] invalid login redirect

[ ] be able to assign classes to students

[ ] make it so you can add class details on calendar [for tutor], and request changes [for tutee] using jinja
    [ ] add class details to SQL database
    [ ] retrieve from SQL database [use RDBS to find all dates i guess]
    [ ] send to template

[ ] add unique pages depending on username

[X] add + link homework page
should be able to:
[ ] upload multiple files
[ ] download, upload, & delete view files

[X] implement file uploads
- store on local file system
- store the link to it on the database

**Non-Functional**

[X] do smooth file up code for navbar in landing page

[ ] format the nice dateInfo for the calendar

[ ] fix double scrollbar issue [WHERE IS IT]

[ ] graphic design for landing pages

[ ] graphic designs for icons
