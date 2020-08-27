from .LibraryManagementViews import libraryManager
from database.tables import User, BlacklistToken
from api import db, bcrypt, app, token
import bcrypt
from flask import request, make_response, jsonify
from flask.views import MethodView
import logging

import pathlib
import sys
currentPath = pathlib.Path(__file__).parent.absolute()
parentdir = currentPath.parent.absolute()
sys.path.insert(0, parentdir)

class LoginAPI(MethodView):
    """
    User Login Resource
    """
    def post(self):
        # get the post data
        password = request.form.get('password')
        nickname = request.form.get('nickname')
        session = db.OpenSession()
        try:
            # fetch the user data
            user = session.query(User).filter_by(
                nickname=nickname
            ).first()
            if user and bcrypt.checkpw(
                password.encode('utf-8'), user.password.encode('utf-8')
            ):
                auth_token = token.encode_auth_token(user.id)
                if auth_token:
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'User does not exist.'
                }
                return make_response(jsonify(responseObject)), 404
        except Exception:
            logging.exception('')
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return make_response(jsonify(responseObject)), 500

class LogoutAPI(MethodView):
    """
    Logout Resource
    """
    def post(self):
        # get auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''
        if auth_token:
            resp = token.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=auth_token)
                try:
                    # insert the token
                    db.session.add(blacklist_token)
                    db.session.commit()
                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    }
                    return make_response(jsonify(responseObject)), 200
                except Exception as e:
                    responseObject = {
                        'status': 'fail',
                        'message': e
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 403

login_view = LoginAPI.as_view('login_api')
logout_view = LogoutAPI.as_view('logout_api')

libraryManager.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)
libraryManager.add_url_rule(
    '/auth/logout',
    view_func=logout_view,
    methods=['POST']
)
