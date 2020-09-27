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

BorrowingDays = 8

class BorrowView(MethodView):
    """
    Borrowing Resource
    """
    def get(self, id=None, field=None, value=None, page=1, itensPerPage=10):
        try:
            requesterId = token.hasValidToken(request.headers.get('Authorization'))
            if not isinstance(requesterId, int):
                responseObject = {
                'status': 'forbidden',
                'message': 'Invalid Token'
                }
                return make_response(jsonify(responseObject)), 401
            if not ( requesterId == id or token.IsAdmin(requesterId)):
                responseObject = {
                    'status': 'forbidden',
                    'message': 'You have no permission to perform this search'
                }
                return make_response(jsonify(responseObject)), 401

            if not ( id or field):
                borrowings = self.__SearchAllBorrowings() 
            elif id:
                borrowings = self.__SearchBorrowingById(id)
            elif field:
                borrowings = self.__SearchBorrowingByFieldAndValue(field, value)
            else:
                responseObject = {
                'status': 'forbidden',
                'message': 'Invalid Search'
                }
                return make_response(jsonify(responseObject)), 401
            res = {}
            for borrowing in borrowings:
                res[borrowing.id] = {
                    'user': self.__getUser(borrowing.user),
                    'book' : self.__getBook(borrowing.book),
                    'borrowingdate' : borrowing.borrowingdate,
                    'returned' : borrowing.returned,
                    'requestedreturndate' : borrowing.requestedreturndate,
                    'actualreturndate' : borrowing.actualreturndate
                }
            return jsonify(res)
        except:
            logging.exception('')
            responseObject = {
                'status': 'fail',
                'message': 'Failed to search Books.'
            }
            return make_response(jsonify(responseObject)), 500
    
    def __SearchAllBorrowings(self):
        try:
             session = db.OpenSession()
             return session.query(Borrowing)
        except:
            logging.exception('')
            return None
    
    def __SearchBorrowingById(self, id):
        try:
            session = db.OpenSession()
            return session.query(Borrowing).filter_by(id=id)
        except:
            logging.exception('')
            return None
    
    def __SearchBorrowingByFieldAndValue(self, field, value):
        try:
            session = db.OpenSession()
            if field == "user":
                return session.query(Borrowing).filter_by(user=value)
            elif field == "book":
                return session.query(Borrowing).filter_by(book=value)
            elif field == "borrowingdate":
                return session.query(Borrowing).filter_by(borrowingdate=datetime.strptime(value, '%d-%m-%Y'))
            elif field == "returned":
                return session.query(Borrowing).filter_by(returned=value)
            elif field == "requestedreturndate":
                return session.query(Borrowing).filter_by(requestedreturndate=datetime.strptime(value, '%d-%m-%Y'))
            elif field == "actualreturndate":
                return session.query(Borrowing).filter_by(actualreturndate=datetime.strptime(value, '%d-%m-%Y'))
            return None
        except:
            logging.exception('')
            return None

    def __getBook(self, bookId):
        try:
            session = db.OpenSession()
            book = session.query(Book).filter_by(id=bookId).first()
            return {
                "id": book.id,
                "title": book.title,
                "publisher": book.publisher,
                "isbn": book.isbn
                }
        except:
            logging.exception('')
            return {}

    def __getUser(self, userId):
        try:
            session = db.OpenSession()
            user = session.query(User).filter_by(id=userId).first()
            return {
                "id": user.id,
                "nickname": user.nickname,
                "fullname": user.fullname,
                "phone": user.phone,
                "email": user.email
            }
        except:
            logging.exception('')
            return {}

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
            failedBorrowings = []
            successfulborrowings = {}
            borrowings = request.get_json()['borrowings']
            for borrowing in borrowings:
                borrowingId, newBorrowing = self.__CreateBorrowing(borrowing)
                if not borrowingId:
                    failedBorrowings.append(borrowing)
                else:
                    successfulborrowings[borrowingId] = newBorrowing

            if len(failedBorrowings) == len(borrowings):
                responseObject = {
                    'status': 'fail',
                    'message': 'Failed to create Borrowing Requests.'
                }
                return make_response(jsonify(responseObject)), 500
            elif len(failedBorrowings) > 0:
                responseObject = {
                    'status': 'Success',
                    'message': 'Some borrowings could not be added to database.',
                    'failedborrowings':failedBorrowings,
                    'successfulborrowings': successfulborrowings
                }
                return make_response(jsonify(responseObject)), 201

            responseObject = {
                'status': 'Success',
                'message': 'Borrowings Created',
                'successfulborrowings': successfulborrowings
            }
            return make_response(jsonify(responseObject)), 201
        except:
            logging.exception('')
            responseObject = {
                'status': 'fail',
                'message': 'Failed to create Borrowings.'
            }
            return make_response(jsonify(responseObject)), 500
    
    def __CreateBorrowing(self, borrowingRequest):
        try:
            session = db.OpenSession()
            book = session.query(Book).filter_by(id=borrowingRequest["book"]).first()
            user = session.query(User).filter_by(id=borrowingRequest["user"]).first()
            if book.availablequantity == 0:
                return None, {}
            newBorrowing = Borrowing(user.id, book.id,date.now(),False,datetime.today()+timedelta(days=BorrowingDays))
            book.availablequantity -= 1
            user.totalborrowedbooks += 1
            user.currentborrowedbooks += 1
            session.add(newBorrowing)
            session.commit()
            return newBorrowing.id, {"user": newBorrowing.user,
                                     "book": newBorrowing.book,
                                     "borrowingdate":  newBorrowing.borrowingdate,
                                     "returned": newBorrowing.returned,
                                     "requestedreturndate": newBorrowing.requestedreturndate }
        except:
            logging.exception('')
            return None, {}

borrow_view =  BorrowView.as_view('borrow_view')

libraryManager.add_url_rule(
    '/borrow', 
    view_func=borrow_view, 
    methods=['GET', 'POST']
)
libraryManager.add_url_rule(
    '/borrow/<int:id>', 
    view_func=borrow_view, 
    methods=['GET']
)
libraryManager.add_url_rule(
    '/borrow/<field>&<value>', 
    view_func=borrow_view, 
    methods=['GET']
)