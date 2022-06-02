import os
import random
import string
import urllib.parse

import requests
from flask import Flask, session, redirect, request

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


@app.route('/login')
def login():
    state = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(30))
    session['state'] = state
    redirect_uri = urllib.parse.quote_plus(os.environ.get('CALLBACK_URL'))
    return redirect(f"{os.environ.get('AUTH_URL')}?response_type=code&client_id={os.environ.get('CLIENT_ID')}&redirect_uri={redirect_uri}&state={state}")


@app.route('/callback')
def callback():
    state = request.args.get('state')
    code = request.args.get('code')

    if session['state'] != state:
        return "Error: State did not match"

    r = requests.post(os.environ.get('TOKEN_URL'), data={'code': code, 'client_id': os.environ.get('CLIENT_ID'), 'client_secret': os.environ.get('CLIENT_SECRET'), 'redirect_uri': os.environ.get('CALLBACK_URL'), 'grant_type': 'authorization_code'}, headers={'Accept': 'application/json'})
    r.raise_for_status()

    data = r.json()
    return "Login successful"
