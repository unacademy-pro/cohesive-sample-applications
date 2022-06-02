import json
import os

import requests
from flask import Flask, request, Response
from flask_httpauth import HTTPTokenAuth
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base, OAuth2App

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
auth = HTTPTokenAuth(scheme='Bearer')

engine = create_engine(f"mysql+pymysql://{os.environ.get('DB_USERNAME')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOSTNAME')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_DATABASE')}", echo=True, future=True)
Base.metadata.create_all(engine)


@auth.verify_token
def verify_token(token):
    if token == os.environ.get("AUTH_TOKEN"):
        return "Authenticated User"


@app.route('/oauth2/provision', methods=['POST', 'DELETE'])
@auth.login_required
def oauth2_provision():
    project = request.args.get('project')
    environment = request.args.get('environment')
    name = request.args.get('name')
    owner = f"{project}-{environment}-{name}"

    if request.method == 'POST':
        data = request.get_json(force=True)
        proxy_url = data['params']['url']

        with Session(engine) as session:
            result = session.query(OAuth2App).filter_by(owner=owner).first()
            if result is None:
                result = session.query(OAuth2App).filter_by(owner=None).first()
                if result is None:
                    return "No apps available", 423
                result.owner = owner
                result.proxy_url = proxy_url
                session.commit()

            return json.dumps({
                "CLIENT_ID": result.client_id,
                "CLIENT_SECRET": result.client_secret,
                "CALLBACK_URL": result.callback_url,
                "AUTH_URL": result.auth_url,
                "TOKEN_URL": result.token_url,
            })

    if request.method == 'DELETE':
        with Session(engine) as session:
            result = session.query(OAuth2App).filter_by(owner=owner).first()
            if result is not None:
                result.owner = None
                result.proxy_url = None
            session.commit()

        return "Success"

    return "Method not supported", 405


@app.route('/oauth2/callback/<name>')
def callback(name):
    with Session(engine) as session:
        result = session.query(OAuth2App).filter_by(name=name).first()
        if result is None:
            return "Not Found", 404
        if result.proxy_url is None:
            return "Proxy URL missing", 500

        proxy_url = result.proxy_url

    resp = requests.request(
        method=request.method,
        url=f"{proxy_url}?{request.query_string.decode('UTF-8')}",
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response
