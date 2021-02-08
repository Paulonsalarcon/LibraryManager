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
from database.tables import User, Book, Borrowing, Reservation
from .LibraryManagementViews import libraryManager

class ReservationView(MethodView):
    """
    Book Reservation Resource
    """
    def post(self):
        requesterId = token.hasValidToken(request.headers.get('Authorization'))
            if not isinstance(requesterId, int):
                responseObject = {
                'status': 'forbidden',
                'message': 'Invalid Token'
                }
                return make_response(jsonify(responseObject)), 401

            reservations = request.get_json()['reservations']
            successfulreservation, failedreservation = self.__ReserveBooks(reservations)

            if len(failedreservation) == len(reservations):
                responseObject = {
                    'status': 'fail',
                    'message': 'Failed to reserve books.'
                }
                return make_response(jsonify(responseObject)), 500
            elif len(failedreservation) > 0:
                responseObject = {
                    'status': 'Success',
                    'message': 'Some books could not be reserved.',
                    'failedreservations':failedreservation,
                    'successfulreservations': successfulreservation
                }
                return make_response(jsonify(responseObject)), 201
            responseObject = {
                'status': 'Success',
                'message': 'Books reserved.',
                'successfulreservations': successfulreservation
            }
            return make_response(jsonify(responseObject)), 200
        except:
            logging.exception('')
            responseObject = {
                'status': 'fail',
                'message': 'Failed to renew Borrowings.'
            }
            return make_response(jsonify(responseObject)), 500
        
    def __ReserveBooks(self,reservations):
        failedReservations = []
        successfulReservations = {}
        for reservation in reservations:
            successfulReservation = self.__ReserveBook(reservation)
            if not successfulReservation:
                failedRenews.append(reservation)
                continue
            successfulReservations[successfulReservation.id] = {
                successfulReservation.user,
                successfulReservation.book,
                successfulReservation.active,
                successfulReservation.reservationdate,
                successfulReservation.nextavailabledate
            }
        return successfulRenews, failedRenews