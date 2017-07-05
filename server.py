import falcon
import json
from datetime import datetime
import os
from tinydb import TinyDB, where


def get_db():
    db_path = 'db.json'
    if not os.path.exists(db_path):
        os.mknod(db_path)
    return TinyDB(db_path)


def register_user(username, password):
    user = find_user(username)
    if user is None:
        get_db().insert({
            'username': username,
            'password': password,
            'registered': str(datetime.now())
        })
    else:
        raise falcon.HTTPBadRequest('User already exists')


def login(username, password, ip):
    user = find_user(username)
    if user is None:
        raise falcon.HTTPBadRequest('User does not exist')
    else:
        if password != user['password']:
            raise falcon.HTTPBadRequest('Incorrect password')
        else:
            return log(user, ip)


def log(user, ip):
    if 'logs' in user:
        logs = user['logs']
    else:
        logs = {}
    logs[str(datetime.now())] = ip
    get_db().update({'logs': logs}, where('username') == user['username'])
    return list(logs.items())


def find_user(username):
    users = get_db().search(where('username') == username)
    if len(users) > 0:
        return users[0]
    else:
        return None


class RegistrationResource:
    def on_post(self, req, resp):
        username = req.get_param('username')
        password = req.get_param('password')
        register_user(username, password)
        resp.body = json.dumps(req.get_param('username'))


class LoginResource:
    def on_post(self, req, resp):
        username = req.get_param('username')
        password = req.get_param('password')
        ip = req.remote_addr
        logs = login(username, password, ip)
        resp.body = json.dumps(logs)


def create():
    x = falcon.API()
    x.add_route('/register', RegistrationResource())
    x.add_route('/login', LoginResource())
    return x


api = create()
