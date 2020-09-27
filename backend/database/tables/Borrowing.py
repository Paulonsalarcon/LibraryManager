from sqlalchemy import Column, Integer, String, Sequence, Table, UniqueConstraint, ForeignKey, Date, Boolean
from .Utils import *
from .Base import *
import logging

class Borrowing(Base):
    __tablename__ = 'borrowings'
    
    id = Column(Integer,  Sequence('borrowing_id_seq'), primary_key=True)
    user = Column(Integer, ForeignKey("users.id"), nullable=False)
    book = Column(Integer, ForeignKey("books.id"), nullable=False)
    borrowingdate = Column(Date, nullable=False)
    returned = Column(Boolean)
    requestedreturndate = Column(Date)
    actualreturndate = Column(Date)

    def __init__(self, user=None, book=None, borrowingdate=None, returned=None, requestedreturndate=None, actualreturndate=None):
        self.user = user
        self.book = book
        self.borrowingdate = borrowingdate
        self.returned = returned
        self.requestedreturndate = requestedreturndate
        self.actualreturndate = actualreturndate

    

    def __repr__(self):
        return "<Borrowing(user='%d', book='%d', borrowingdate='%s', returned='%b', requestedreturndate='%s', actualreturndate='%s')>" % (
                                  self.user, self.book, self.borrowingdate,
                                  self.returned, self.requestedreturndate, self.actualreturndate)

    def create(self, engine, meta):
        logging.debug("Creating Table Borrowings")
        borrowing = Table(self.__tablename__, meta,
        Column('id', Integer,  Sequence('borrowing_id_seq'), primary_key=True),
        Column('user',Integer, ForeignKey("users.id"), nullable=False),
        Column('book',Integer, ForeignKey("books.id"), nullable=False),
        Column('borrowingdate', Date, nullable=False),
        Column('returned', Boolean),
        Column('requestedreturndate', Date),
        Column('actualreturndate', Date),
        extend_existing=True
        )
        try:
            borrowing.create(engine)
            logging.info("Table Borrowings Created")
        except:
            logging.error("Failed Create Borrowings Table")