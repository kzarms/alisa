from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Yo yo yo yo yo! This is my world!"