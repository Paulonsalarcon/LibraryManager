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

BorrowingDays = 9

class RenewView(MethodView):
    """
    Renew Borrowing Resource
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
            successfulrenew, failedrenew = self.__RenewBorrowings(borrowings)

            if len(failedrenew) == len(borrowings):
                responseObject = {
                    'status': 'fail',
                    'message': 'Failed to renew Borrowings.'
                }
                return make_response(jsonify(responseObject)), 500
            elif len(failedrenew) > 0:
                responseObject = {
                    'status': 'Success',
                    'message': 'Some borrowings could not be renewed.',
                    'failedborrowings':failedrenew,
                    'successfulborrowings': successfulrenew
                }
                return make_response(jsonify(responseObject)), 201
            responseObject = {
                'status': 'Success',
                'message': 'Borrowings Renewed.',
                'successfulborrowings': successfulrenew
            }
            return make_response(jsonify(responseObject)), 200
        except:
            logging.exception('')
            responseObject = {
                'status': 'fail',
                'message': 'Failed to renew Borrowings.'
            }
            return make_response(jsonify(responseObject)), 500
    
    def __RenewBorrowings(self, borrowings):
        failedRenews = []
        successfulRenews = {}
        for borrowingId in borrowings:
            successfulRenew = self.__RenewBorrowing(borrowingId)
            if not successfulRenew:
                failedRenews.append(borrowingId)
                continue
            successfulRenews[borrowingId] = successfulRenew
        return successfulRenews, failedRenews

    def __RenewBorrowing(self, borrowingId):
        try:
            session = db.OpenSession()
            borrowing = session.query(Borrowing).filter_by(id=borrowingId).first()
            if borrowing.returned:
                message = "Already returned"
            else:
                borrowing.returned = True
                borrowing.requestedreturndate = date.today()+timedelta(days=BorrowingDays)
                message = "Renewed"
            session.commit()
            successfulRenew = {
                "message": message,
                "user": borrowing.user,
                "book": borrowing.book,
                "requestedreturndate": borrowing.requestedreturndate
            }
            session.close()
            return successfulRenew
        except:
            logging.exception('')
            return {}

renew_view =  RenewView.as_view('renew_view')

libraryManager.add_url_rule(
    '/renew', 
    view_func=renew_view, 
    methods=['POST']
)