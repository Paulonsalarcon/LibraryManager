import pathlib, sys
currentPath = pathlib.Path(__file__).parent.absolute()
parentdir = currentPath.parent.absolute()
sys.path.insert(0,parentdir) 

import json
from datetime import date, timedelta, datetime
from flask import request, make_response, jsonify, abort
from flask.views import MethodView
from api import db, token, bcrypt
import logging
from database.tables import User, Book, Borrowing
from .LibraryManagementViews import libraryManager

class ReturnView(MethodView):
    """
    Return Borrowing Resource
    """
    def post(self):
        try:
            requesterId = token.hasValidToken(request.headers.get('Authorization'))
            if not isinstance(requesterId, int):
                responseObject = {
                'status': 'forbidden',
                'message': 'Invalid Token'
                }
                return make_response(jsonify(responseObject)), 401

            if not token.IsAdmin(requesterId):
                responseObject = {
                'status': 'forbidden',
                'message': 'Your user does not have permission to perform this action.'
                }
                return make_response(jsonify(responseObject)), 401
            borrowings = request.get_json()['borrowings']
            successfulreturn, failedreturn = self.__ReturnBorrowings(borrowings)

            if len(failedreturn) == len(borrowings):
                responseObject = {
                    'status': 'fail',
                    'message': 'Failed to return Borrowings.'
                }
                return make_response(jsonify(responseObject)), 500
            elif len(failedreturn) > 0:
                responseObject = {
                    'status': 'Success',
                    'message': 'Some borrowings could not be returned.',
                    'failedborrowings':failedreturn,
                    'successfulborrowings': successfulreturn
                }
                return make_response(jsonify(responseObject)), 201
            responseObject = {
                'status': 'Success',
                'message': 'Borrowings Returned.',
                'successfulborrowings': successfulreturn
            }
            return make_response(jsonify(responseObject)), 200
        except:
            logging.exception('')
            responseObject = {
                'status': 'fail',
                'message': 'Failed to return Borrowings.'
            }
            return make_response(jsonify(responseObject)), 500
    
    def __ReturnBorrowings(self, borrowings):
        failedReturns = []
        successfulReturns = {}
        for borrowingId in borrowings:
            successfulReturn = self.__ReturnBorrowing(borrowingId)
            if not successfulReturn:
                failedReturns.append(borrowingId)
                continue
            successfulReturns[borrowingId] = successfulReturn
        return successfulReturns, failedReturns

    def __ReturnBorrowing(self, borrowingId):
        try:
            session = db.OpenSession()
            borrowing = session.query(Borrowing).filter_by(id=borrowingId).first()
            if borrowing.returned:
                message = "Already returned"
            else:
                borrowing.returned = True
                borrowing.actualreturndate = date.today()
                message = "Returned"
                user = session.query(User).filter_by(id=borrowing.user).first()
                user.currentborrowedbooks -= 1
                book = session.query(Book).filter_by(id=borrowing.book).first()
                book.availablequantity += 1
            session.commit()
            successfulReturn = {
                "message": message,
                "user": borrowing.user,
                "book": borrowing.book,
                "returned": borrowing.returned,
                "actualreturndate": borrowing.actualreturndate
            }
            session.close()
            return successfulReturn
        except:
            logging.exception('')
            return {}

return_view =  ReturnView.as_view('return_view')

libraryManager.add_url_rule(
    '/return', 
    view_func=return_view, 
    methods=['POST']
)