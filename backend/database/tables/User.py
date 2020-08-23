from sqlalchemy import Column, Integer, String, Sequence, Table, UniqueConstraint
from .Utils import *
from .Base import *
import logging

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer,  Sequence('user_id_seq'), primary_key=True)
    fullname = Column(String(50), nullable=False)
    nickname = Column(String(50), nullable=False)
    password = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)
    totalborrowedbooks = Column(Integer)
    currentborrowedbooks = Column(Integer)
    reservedbooks = Column(Integer)

    def __init__(self, fullname=None, nickname=None, phone=None, email=None, role=None, password=None, totalborrowedbooks=None, currentborrowedbooks=None, reservedbooks=None):
        self.fullname = fullname
        self.nickname = nickname
        self.phone = phone
        self.email = email
        self.role = role
        self.password = password
        self.totalborrowedbooks = totalborrowedbooks
        self.currentborrowedbooks = currentborrowedbooks
        self.reservedbooks = reservedbooks


    def __repr__(self):
        return "<User(fullname='%s', nickname='%s', password='%s', phone='%s', email='%s', role='%s', totalborrowedbooks='%d', currentborrowedbooks='%d', reservedbooks='%d')>" % (
                                  self.fullname, self.nickname, self.password,
                                  self.phone, self.email, self.role,
                                  self.totalborrowedbooks, self.currentborrowedbooks, self.reservedbooks)

    def create(self, engine, meta):
        logging.debug("Creating Table Users")
        user = Table(self.__tablename__, meta,
        Column('id',Integer,  Sequence('user_id_seq'), primary_key=True),
        Column('fullname', String(50), nullable=False),
        Column('nickname', String(50), nullable=False),
        Column('password', String(50), nullable=False),
        Column('phone', String(50), nullable=False),
        Column('email', String(50), nullable=False),
        Column('role', String(50), nullable=False),
        Column('totalborrowedbooks', Integer),
        Column('currentborrowedbooks', Integer),
        Column('reservedbooks', Integer),
        UniqueConstraint('nickname'),
        extend_existing=True
        )
        try:
            user.create(engine)
            logging.info("Table Users Created")
        except:
            logging.error("Failed Create Table Users")
    
    #Migration
    def addColumn(self,engine,column):
        add_column(engine, self.__tablename__, column)

    
    def addReservedBooksColumn(self, engine):
        logging.debug("Adding ReservedBooks Column to Table Users")
        try:
            self.addColumn(engine,Column('reservedbooks', Integer))
            logging.info("ReservedBooks Column Added to Table Users")
        except:
            logging.error("Failed Add ReservedBooks Column to Table Users")

    def migrate(self, engine):
        logging.info("Starting Migration for Table Users")
        self.addReservedBooksColumn(engine)
        logging.info("Migration for Table Users Done")