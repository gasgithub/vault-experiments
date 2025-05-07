import os
import requests
import json
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

@app.route('/rest')
def vault_rest():

    VAULT_ADDR = os.environ.get('VAULT_ADDR', 'http://vault:8200')
    JWT_PATH = os.environ.get('JWT_PATH', '/var/run/secrets/kubernetes.io/serviceaccount/token')
    with open(JWT_PATH, 'r') as file:
        token = file.read()

    print("token: ", token)

    headers = {
        "accept": "application/json",
        "X-Vault-Token": token
    }

    vault_url = VAULT_ADDR + '/v1/dev-secrets/data/app1/config'

    token_response = requests.get(vault_url, headers = headers, timeout=600)

    print("token_response: ", token_response)
    json_response = json.loads(token_response.text)

    print("json_response", json_response)

    username = json_response['data']['data']['username']
    password = json_response['data']['data']['password']

    secrets = []

    secrets.append(username)
    secrets.append(password)

    return render_template("index.html", secrets=secrets)