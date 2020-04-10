from sqlalchemy import Column, Integer, String, Sequence, Table, UniqueConstraint
from .Utils import *
from .Base import *
import logging

class Author(Base):
    __tablename__ = 'authors'
    
    id = Column(Integer,  Sequence('author_id_seq'), primary_key=True)
    fullname = Column(String(50), nullable=False)
    nickname = Column(String(50), nullable=False)
    authortype = Column(String(50))

    def __repr__(self):
        return "<Author(fullname='%s', nickname='%s', authortype='%s')>" % (
                                  self.name, self.fullname, self.nickname,
                                  self.authortype)

    def create(self, engine, meta):
        logging.debug("Creating Table Authors")
        author = Table(self.__tablename__, meta,
        Column('id',Integer,  Sequence('author_id_seq'), primary_key=True),
        Column('fullname', String(50), nullable=False),
        Column('nickname', String(50), nullable=False),
        Column('authortype', String(50)),
        UniqueConstraint('fullname'),
        extend_existing=True
        )
        try:
            author.create(engine)
            logging.info("Table Authors Created")
        except:
            logging.error("Failed Create Authors Table")
    
    #Migration
    def addColumn(self,engine,column):
        add_column(engine, self.__tablename__, column)

    def migrate(self, engine):
        logging.info("Starting Migration for Table Authors")
        logging.info("Migration for Table Authors Done")