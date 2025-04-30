import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')

def hello_world():

    secrets = []
    username = os.environ.get('username', 'undefinded')
    password = os.environ.get('password', 'undefinded')
    secrets.append(username)
    secrets.append(password)

    return render_template("index.html", secrets=secrets)