import pathlib, sys
currentPath = pathlib.Path(__file__).parent.absolute()
parentdir = currentPath.parent.absolute()
sys.path.insert(0,parentdir) 

import json
from flask import request, make_response, jsonify, abort
from flask.views import MethodView
from api import db, token, bcrypt
import bcrypt
import logging
from database.tables import User
from .LibraryManagementViews import libraryManager

class UserView(MethodView):
    """
    User Resource
    """

    def get(self, id=None, field=None, value=None, page=1, itensPerPage=10):
        session = db.OpenSession()
         # get the auth token
        
        if isinstance(token.hasValidToken(request.headers.get('Authorization')), int):
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
                res = {}
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
        responseObject = {
                'status': 'forbidden',
                'message': 'Invalid Token.'
            }
        return make_response(jsonify(responseObject)), 401

    def post(self):
        try:
            session = db.OpenSession()
            requesterId = token.hasValidToken(request.headers.get('Authorization'))
        
            if isinstance(requesterId, int):
                user = session.query(User).filter_by(id=requesterId).first()
                if user.role=="admin":
                    role = request.form.get('role')
                else:
                    role="client"
            else:
                role="client"

            fullname = request.form.get('fullname')
            nickname = request.form.get('nickname')
            password =  bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            phone = request.form.get('phone')
            email = request.form.get('email')
        
            newUser = User(fullname, nickname, phone, email, role, password)

            session.add(newUser)
            session.commit()
            return jsonify({newUser.id: {
                'fullname': newUser.fullname,
                'nickname': newUser.nickname,
                'phone': newUser.phone,
                'email': newUser.email,
                'role': newUser.role,
            }})
        except:
            logging.exception('')
            responseObject = {
                'status': 'fail',
                'message': 'Failed to create new user.'
            }
        return make_response(jsonify(responseObject)), 500
    
user_view =  UserView.as_view('user_view')
libraryManager.add_url_rule(
    '/user', 
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