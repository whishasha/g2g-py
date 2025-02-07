from flask import Flask, render_template
from waitress import serve

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/inquire")
def inquire():
    return render_template('inquire.html')

@app.route("/test")
def test():
    return render_template('renamethis.html')

@app.route("/user/home")
def user_home():
    return render_template('user_home.html')

@app.route("/user/timetable")
def user_timetable():
    return render_template('user_timetable.html')

mode = "dev"
if mode == "prod":
    serve(app, port=10000)
elif mode == "dev":
    app.run(host="0.0.0.0", port=10000, debug=True) 