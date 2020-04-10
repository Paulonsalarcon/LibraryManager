from sqlalchemy import Column, Integer, String, Sequence, Table, UniqueConstraint, ForeignKey, Date
from .Utils import *
from .Base import *
import logging

class LibraryHistory(Base):
    __tablename__ = 'libraryhistory'
    
    id = Column(Integer,  Sequence('libraryhistory_id_seq'), primary_key=True)
    measurementdate = Column(Date, nullable=False)
    users = Column(Integer)
    books = Column(Integer)
    borrowedbooks = Column(Integer)
    dalayedborrowings = Column(Integer)
    borrowingsdue = Column(Integer)
    reservedbooks = Column(Integer)
    

    def __repr__(self):
        return "<Borrowing(measurementdate='%s', users='%d', books='%d', borrowedbooks='%d', delayedborrowings='%d', borrowingsdue='%d', reservedbooks='%d')>" % (
                                  self.measurementdate, self.users, self.books,
                                  self.borrowedbooks, self.dalayedborrowings, self.borrowingsdue,
                                  self.reservedbooks)

    def create(self, engine, meta):
        logging.debug("Creating Table LibraryHistory")
        borrowing = Table(self.__tablename__, meta,
        Column('id', Integer,  Sequence('libraryhistory_id_seq'), primary_key=True),
        Column('measurementdate', Date, nullable=False),
        Column('users', Integer),
        Column('books', Integer),
        Column('borrowedbooks', Integer),
        Column('dalayedborrowings', Integer),
        Column('borrowingsdue', Integer),
        Column('reservedbooks', Integer),
        extend_existing=True
        )
        try:
            borrowing.create(engine)
            logging.info("Table LibraryHistory Created")
        except:
            logging.error("Failed Create LibraryHistory Table")