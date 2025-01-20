from flask import Flask
from waitress import serve

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

mode = "prod"
if mode == "prod":
    serve(app, port=10000)
elif mode == "dev":
    app.run(host="0.0.0.0", port=10000, debug=True) 