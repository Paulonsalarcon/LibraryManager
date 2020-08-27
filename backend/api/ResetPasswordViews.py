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

class ResetPassword(MethodView):
    def post(self,nickname=None):
        session = db.OpenSession()
        requesterId = token.hasValidToken(request.headers.get('Authorization'))
        
        if not isinstance(requesterId, int):
            responseObject = {
            'status': 'forbidden',
            'message': 'Invalid Token'
            }
            return make_response(jsonify(responseObject)), 401
        user = session.query(User).filter_by(id=requesterId).first()
        if not ((user.nickname==nickname) and (user.role=="admin")):
            responseObject = {
            'status': 'forbidden',
            'message': 'Your user does not have permission to perform this action.'
            }
            return make_response(jsonify(responseObject)), 401
        
        try:
            user = session.query(User).filter_by(nickname=nickname).first()

            user.password = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
            session.commit()

            responseObject = {
                'status': 'Success',
                'message': 'Password Successfully Updated.'
            }
            return make_response(jsonify(responseObject)), 200

        except Exception:
            logging.exception('')
            responseObject = {
                'status': 'fail',
                'message': 'Password Redefinition Failed'
            }
            return make_response(jsonify(responseObject)), 500


resetPassword_view = ResetPassword.as_view('reset_password')

libraryManager.add_url_rule(
    '/resetpassword/<nickname>',
    view_func=resetPassword_view,
    methods=['POST']
)