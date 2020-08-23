import pathlib, sys
currentPath = pathlib.Path(__file__).parent.absolute()
parentdir = currentPath.parent.absolute()
sys.path.insert(0,parentdir) 

import json
from flask import request, jsonify, abort
from flask.views import MethodView
from api import db
from database.tables import User
from .LibraryManagementViews import libraryManager

class UserAPI(MethodView):
    """
    User Resource
    """
    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.'
                }
                return make_response(jsonify(responseObject)), 401
        else:
            auth_token = ''
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                responseObject = {
                    'status': 'success',
                    'data': {
                        'user_id': user.id,
                        'email': user.email,
                        'admin': user.admin,
                        'registered_on': user.registered_on
                    }
                }
                return make_response(jsonify(responseObject)), 200
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
            return make_response(jsonify(responseObject)), 401

class UserView(MethodView):
    def get(self, id=None, field=None, value=None, page=1, itensPerPage=10):
        session = db.OpenSession()
        if (not id) and (not field):
            users = session.query(User)
            res = {}
            for user in users:
                res[user.id] = {
                    'fullname': user.fullname,
                    'nickname': user.nickname,
                    'phone': user.phone,
                    'email': user.email,
                    'role': user.role,
                    'totalborrowedbooks': str(user.totalborrowedbooks),
                    'currentborrowedbooks': str(user.currentborrowedbooks),
                    'reservedbooks': str(user.reservedbooks)
                }
        elif not id:
            if field == 'fullname':
                users = session.query(User).filter_by(fullname=value)
            elif field == 'nickname':
                users = session.query(User).filter_by(nickname=value).first()
            elif field == 'phone':
                users = session.query(User).filter_by(phone=value)
            elif field == 'email':
                users = session.query(User).filter_by(email=value)
            elif field == 'role':
                users = session.query(User).filter_by(role=value)
            elif field == 'totalborrowedbooks':
                users = session.query(User).filter_by(totalborrowedbooks=int(value))
            elif field == 'currentborrowedbooks':
                users = session.query(User).filter_by(currentborrowedbooks=int(value))
            elif field == 'reservedbooks':
                users = session.query(User).filter_by(reservedbooks=int(value))
            else:
                abort(404)
            if not users:
                abort(404)
            res = {}
            for user in users:
                res[user.id] = {
                    'fullname': user.fullname,
                    'nickname': user.nickname,
                    'phone': user.phone,
                    'email': user.email,
                    'role': user.role,
                    'totalborrowedbooks': str(user.totalborrowedbooks),
                    'currentborrowedbooks': str(user.currentborrowedbooks),
                    'reservedbooks': str(user.reservedbooks)
                }
        else:
            user = session.query(User).filter_by(id=id).first()
            if not user:
                abort(404)
            res[user.id] = {
                'fullname': user.fullname,
                'nickname': user.nickname,
                'phone': user.phone,
                'email': user.email,
                'role': user.role,
                'totalborrowedbooks': str(user.totalborrowedbooks),
                'currentborrowedbooks': str(user.currentborrowedbooks),
                'reservedbooks': str(user.reservedbooks)
            }
        return jsonify(res)

    def post(self):
        fullname = request.form.get('fullname')
        nickname = request.form.get('nickname')
        password = request.form.get('password')
        phone = request.form.get('phone')
        email = request.form.get('email')
        role = request.form.get('role')
        user = User(fullname, nickname, phone, email, role, password)
        session = db.OpenSession()
        session.add(user)
        session.commit()
        return jsonify({user.id: {
            'fullname': user.fullname,
            'nickname': user.nickname,
            'phone': user.phone,
            'email': user.email,
            'role': user.role,
        }})
    
user_view =  UserView.as_view('user_view')
libraryManager.add_url_rule(
    '/user/', 
    view_func=user_view, 
    methods=['GET', 'POST']
)
libraryManager.add_url_rule(
    '/user/<int:id>', 
    view_func=user_view, 
    methods=['GET']
)
libraryManager.add_url_rule(
    '/user/<field>&<value>', 
    view_func=user_view, 
    methods=['GET']
)