from database.tables import BlacklistToken
import datetime
import jwt
import logging

import pathlib
import sys
currentPath = pathlib.Path(__file__).parent.absolute()
parentdir = currentPath.parent.absolute()
sys.path.insert(0, parentdir)

def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp': str(datetime.datetime.utcnow() + datetime.timedelta(days=0, hours=8)),
            'iat': str(datetime.datetime.utcnow()),
            'sub': str(user_id)
        }
        return jwt.encode(
            payload,
            #app.config.get('SECRET_KEY'),
            'secret',
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
        payload = jwt.decode(auth_token, 'secret')
        is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
        if is_blacklisted_token:
            return 'Token blacklisted. Please log in again.'
        else:
            return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


