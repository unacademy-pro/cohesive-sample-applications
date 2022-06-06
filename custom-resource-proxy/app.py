import json
import os

import requests
from flask import Flask, request, Response, redirect
from flask_httpauth import HTTPTokenAuth
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Base, App

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
auth = HTTPTokenAuth(scheme='Bearer')

engine = create_engine(f"mysql+pymysql://{os.environ.get('DB_USERNAME')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOSTNAME')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_DATABASE')}", echo=True, future=True)
Base.metadata.create_all(engine)


@auth.verify_token
def verify_token(token):
    if token == os.environ.get("AUTH_TOKEN"):
        return "Authenticated User"


@app.route('/provision/<resource_type>', methods=['POST', 'DELETE'])
@auth.login_required
def provision(resource_type):
    project = request.args.get('project')
    environment = request.args.get('environment')
    name = request.args.get('name')
    owner = f"{project}-{environment}-{name}"

    if request.method == 'POST':
        data = request.get_json(force=True)
        proxy_url = data['params']['url']
        proxy_type = data['params']['type']

        with Session(engine) as session:
            result = session.query(App).filter_by(owner=owner, resource_type=resource_type).first()
            if result is None:
                result = session.query(App).filter_by(owner=None, resource_type=resource_type).first()
                if result is None:
                    return "No apps available", 423
                result.owner = owner
                result.proxy_url = proxy_url
                result.proxy_type = proxy_type
                session.commit()

            if result.vars is not None and result.vars != "":
                env_vars = json.loads(result.vars)
            else:
                env_vars = {}
            body = {
                "env_vars": env_vars
            }
            response = Response(json.dumps(body), 200, [('Content-Type', "application/json")])
            return response

    if request.method == 'DELETE':
        with Session(engine) as session:
            result = session.query(App).filter_by(owner=owner, resource_type=resource_type).first()
            if result is not None:
                result.owner = None
                result.proxy_url = None
                result.proxy_type = None
            session.commit()

        return "Success"

    return "Method not supported", 405


@app.route('/callback/<resource_type>/<name>')
def callback(resource_type, name):
    with Session(engine) as session:
        result = session.query(App).filter_by(name=name, resource_type=resource_type).first()
        if result is None:
            return "Not Found", 404
        if result.proxy_url is None or result.proxy_url == '':
            return "Proxy URL missing", 500

        proxy_url = result.proxy_url
        proxy_type = result.proxy_type
        session.commit()

    url = f"{proxy_url}?{request.query_string.decode('UTF-8')}"
    print(f"Proxying the request to {url}")

    if proxy_type == 'redirect':
        return redirect(url)
    else:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={key: value for (key, value) in request.headers if key != 'Host' and not key.startswith('X-')},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False)

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]

        response = Response(resp.content, resp.status_code, headers)
        return response
