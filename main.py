from flask import Flask, render_template
from waitress import serve

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/test")
def test():
    return render_template('renamethis.html')

mode = "dev"
if mode == "prod":
    serve(app, port=10000)
elif mode == "dev":
    app.run(host="0.0.0.0", port=10000, debug=True) 