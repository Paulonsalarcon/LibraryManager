from sqlalchemy import Column, Integer, String, Sequence, Table, UniqueConstraint, ForeignKey, Date, Boolean
from .Utils import *
from .Base import *
import logging

class Reservation(Base):
    __tablename__ = 'reservations'
    
    id = Column(Integer,  Sequence('reservation_id_seq'), primary_key=True)
    user = Column(Integer, ForeignKey("users.id"), nullable=False)
    book = Column(Integer, ForeignKey("books.id"), nullable=False)
    reservationdate = Column(Date, nullable=False)
    active = Column(Boolean)
    nextavailabledate = Column(Date)
    

    def __repr__(self):
        return "<Reservation(user='%d', book='%d', reservationdate='%s', active='%b', nextavailabledate='%s')>" % (
                                  self.user, self.book, self.reservationdate,
                                  self.active, self.nextavailabledate)

    def create(self, engine, meta):
        logging.debug("Creating Table Reservations")
        borrowing = Table(self.__tablename__, meta,
        Column('id', Integer,  Sequence('reservation_id_seq'), primary_key=True),
        Column('user',Integer, ForeignKey("users.id"), nullable=False),
        Column('book',Integer, ForeignKey("books.id"), nullable=False),
        Column('reservationdate', Date, nullable=False),
        Column('active', Boolean),
        Column('nextavailabledate', Date),
        extend_existing=True
        )
        try:
            borrowing.create(engine)
            logging.info("Table Reservations Created")
        except:
            logging.error("Failed Create Reservations Table")