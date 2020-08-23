import jwt
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Table, UniqueConstraint
from .Utils import *
from .Base import *
import logging

class BlacklistToken(Base):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(500), unique=True, nullable=False)
    blacklisted_on = Column(DateTime, nullable=False)

    def __init__(self, token=None):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    def create(self, engine, meta):
        logging.debug("Creating Table BlacklistToken")
        blacklistToken = Table(self.__tablename__, meta,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('token', String(500), unique=True, nullable=False),
        Column('blacklisted_on', DateTime, nullable=False),
        extend_existing=True
        )
        try:
            blacklistToken.create(engine)
            logging.info("Table BlacklistToken Created")
        except:
            logging.error("Failed Create Table BlacklistToken")

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

     #Migration
    def addColumn(self,engine,column):
        add_column(engine, self.__tablename__, column)

    def migrate(self, engine):
        logging.info("Starting Migration for Table BlacklistToken")
        logging.info("Migration for Table BlacklistToken Done")
