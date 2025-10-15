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

    VAULT_ADDR = os.environ.get('VAULT_ADDR', 'http://vault.vault.svc.cluster.local:8200')
    JWT_PATH = os.environ.get('JWT_PATH', '/var/run/secrets/kubernetes.io/serviceaccount/token')
    with open(JWT_PATH, 'r') as file:
        token = file.read()

    print("token: ", token)


    login_data = {
        "role": "app2-role",
        "jwt": token
    }
    auth_url = VAULT_ADDR + '/v1/auth/demo-cluster/login'
    headers = {
        "accept": "application/json"
    }

    login_response = requests.post(auth_url, headers = headers, data = login_data)

    print("login_response: ", login_response)
    print("text: ", login_response.text)
    json_login = json.loads(login_response.text)
    print("json_login", json_login)
    client_token = json_login['auth']['client_token']

    print("client_token", client_token)

    headers = {
        "accept": "application/json",
        "X-Vault-Token": client_token
    }
    secret_url = VAULT_ADDR + '/v1/dev-secrets/data/app1/config'

    secret_response = requests.get(secret_url, headers = headers)

    print("secret_response: ", secret_response)
    json_secret = json.loads(secret_response.text)
    print("json_secret", json_secret)    
    username = json_secret['data']['data']['username']
    password = json_secret['data']['data']['password']

    secrets = []

    secrets.append(username)
    secrets.append(password)

    return render_template("index.html", secrets=secrets)