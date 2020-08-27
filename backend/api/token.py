from api import db
from database.tables import BlacklistToken
import datetime
import jwt
import logging

import pathlib
import sys
currentPath = pathlib.Path(__file__).parent.absolute()
parentdir = currentPath.parent.absolute()
sys.path.insert(0, parentdir)

secret_key = "testsecret"

def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=8),
            'iat': datetime.datetime.utcnow(),
            'sub': str(user_id)
        }
        return jwt.encode(
            payload,
            #app.config.get('SECRET_KEY'),
            secret_key,
            algorithm='HS256'
        )
    except Exception as e:
        logging.exception('')
        return e

def decode_auth_token(auth_token):
    """
    Validates the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        #payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
        payload = jwt.decode(auth_token, secret_key,algorithm=['HS256'])
        session = db.OpenSession()
        is_blacklisted_token = BlacklistToken.check_blacklist(session,auth_token)
        if is_blacklisted_token:
            return 'Token blacklisted. Please log in again.'
        else:
            return int(payload['sub'])
    except jwt.ExpiredSignatureError:
        logging.exception('')
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        logging.exception('')
        return 'Invalid token. Please log in again.'

def hasValidToken(auth_header):
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            responseObject = {
                'status': 'forbidden',
                'message': 'Token malformed.'
            }
            return responseObject
    else:
        auth_token = ''
    if auth_token:
        return decode_auth_token(auth_token)
    else:
            responseObject = {
                'status': 'forbidden',
                'message': 'Provide a valid auth token.'
            }
            return responseObject


