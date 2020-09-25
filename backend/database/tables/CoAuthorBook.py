from sqlalchemy import Column, Integer, String, Sequence, Table, UniqueConstraint, ForeignKey
from .Utils import *
from .Base import *
import logging

class CoAuthorBook(Base):
    __tablename__ = 'coauthorbooks'
    
    book = Column(Integer, ForeignKey("books.id"), primary_key=True)
    author = Column(Integer, ForeignKey("authors.id"), primary_key=True)

    def __init__(self,book=None, author=None):
        self.book=book
        self.author=author

    def __repr__(self):
        return "<CoAuthorBook(book='%d', author='%d')>" % (
                                  self.book, self.author)

    def create(self, engine, meta):
        logging.debug("Creating Table CoAuthorBooks")
        coauthorbook = Table(self.__tablename__, meta,
        Column('book',Integer, ForeignKey("books.id"), primary_key=True),
        Column('author',Integer, ForeignKey("authors.id"), primary_key=True),
        extend_existing=True
        )
        try:
            coauthorbook.create(engine)
            logging.info("Table CoAuthorBooks Created")
        except:
            logging.error("Failed Create CoAuthorBooks Table")
    
    #Migration
    def addColumn(self,engine,column):
        add_column(engine, self.__tablename__, column)

    def migrate(self, engine):
        logging.info("Starting Migration for Table CoAuthorBooks")
        logging.info("Migration for Table CoAuthorBooks Done")