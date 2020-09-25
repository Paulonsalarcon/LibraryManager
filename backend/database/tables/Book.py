from sqlalchemy import Column, Integer, String, Sequence, Table, UniqueConstraint, ForeignKey
from .Utils import *
from .Base import *
import logging

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer,  Sequence('book_id_seq'), primary_key=True)
    isbn = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    publisher = Column(String(50), nullable=False)
    firstauthor = Column(Integer, ForeignKey("authors.id"), nullable=False)
    quantity = Column(Integer)
    availablequantity = Column(Integer)
    reservedquantity = Column(Integer)

    def __init__(self, isbn=None, title=None, publisher=None, firstauthor=None,quantity=None, availablequantity=None, reservedquantity=None):
        self.title=title
        self.isbn=isbn
        self.publisher=publisher
        self.firstauthor=firstauthor
        self.quantity=quantity
        self.availablequantity=availablequantity
        self.reservedquantity=reservedquantity

    def __repr__(self):
        return "<Book(isbn='%s', title='%s', publisher='%s', firstauthor='%s', quantity='%d', availablequantity='%d', reservedquantity='%d')>" % (
                                  self.isbn, self.title, self.publisher,
                                  self.firstauthor, self.quantity, self.availablequantity,self.reservedquantity)

    def create(self, engine, meta):
        logging.debug("Creating Table Books")
        book = Table(self.__tablename__, meta,
        Column('id',Integer,  Sequence('book_id_seq'), primary_key=True),
        Column('isbn', String(50), nullable=False),
        Column('title', String(500), nullable=False),
        Column('publisher', String(50), nullable=False),
        Column('firstauthor', Integer, ForeignKey("authors.id"), nullable=False),
        Column('quantity', Integer),
        Column('availablequantity', Integer),
        Column('reservedquantity', Integer),
        UniqueConstraint('isbn'),
        extend_existing=True
        )
        try:
            book.create(engine)
            logging.info("Table Books Created")
        except:
            logging.error("Failed Create Books Table")
    
    #Migration
    def addColumn(self,engine,column):
        add_column(engine, self.__tablename__, column)

    def migrate(self, engine):
        logging.info("Starting Migration for Table Books")
        logging.info("Migration for Table Books Done")