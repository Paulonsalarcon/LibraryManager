import pathlib, sys
currentPath = pathlib.Path(__file__).parent.absolute()
parentdir = currentPath.parent.absolute()
sys.path.insert(0,parentdir) 

import json
from flask import request, make_response, jsonify, abort
from flask.views import MethodView
from api import db, token, bcrypt
import logging
from database.tables import User, Book, Author, CoAuthorBook
from sqlalchemy import or_
from .LibraryManagementViews import libraryManager

class BookView(MethodView):
    """
    Book Resource
    """

    def get(self, id=None, field=None, value=None, page=1, itensPerPage=10):
        try:
            requesterId = token.hasValidToken(request.headers.get('Authorization'))
            if not isinstance(requesterId, int):
                responseObject = {
                'status': 'forbidden',
                'message': 'Invalid Token'
                }
                return make_response(jsonify(responseObject)), 401
            if not ( id or field):
                books = self.SearchAllBooks() 
            elif id:
                books = self.SearchBookById(id)
            elif field:
                books = self.SearchBookByFieldAndValue(field, value)
            else:
                responseObject = {
                'status': 'forbidden',
                'message': 'Invalid Search'
                }
                return make_response(jsonify(responseObject)), 401
            res = {}
            for book in books:
                res[book.id] = {
                    'title': book.title,
                    'isbn' : book.isbn,
                    'publisher' : book.publisher,
                    'author' : self.FindAuthorsByBook(book.id),
                    'quantity' : book.quantity,
                    'availablequantity' : book.availablequantity,
                    'reservedquantity' : book.reservedquantity,
                }
            return jsonify(res)
        except:
                logging.exception('')
                print(books)
                responseObject = {
                    'status': 'fail',
                    'message': 'Failed to search Books.'
                }
                return make_response(jsonify(responseObject)), 500
    def SearchAllBooks(self):
        try:
            session = db.OpenSession()
            return session.query(Book)
        except:
            logging.exception('')
            return None
    
    def SearchBookById(self, id):
        try:
            session = db.OpenSession()
            return session.query(Book).filter_by(id=id)
        except:
            logging.exception('')
            return None
    
    def SearchBookByFieldAndValue(self, field, value):
        value = "%"+value+"%"
        session = db.OpenSession()
        if field == "isbn":
            books = session.query(Book).filter(Book.isbn.ilike(value))
        elif field == "title":
            books = session.query(Book).filter(Book.title.ilike(value))
        elif field == "author":
            books = self.SearchBookByAuthor(value)
        elif field == "publisher":
            books = session.query(Book).filter(Book.publisher.ilike(value))
        else:
            books = None
        session.close()
        return books
 
    def SearchBookByAuthor(self, authorname):
        authorsId = []
        booksId = []
        session = db.OpenSession()
        authors = session.query(Author).filter(Author.fullname.ilike(authorname))
        for author in authors:
            authorsId.append(author.id)
        coauthorsbooks = session.query(CoAuthorBook).filter(CoAuthorBook.author.in_(authorsId))
        for coauthorbook in coauthorsbooks:
            booksId.append(coauthorbook.book)
        return session.query(Book).filter(or_(Book.id.in_(booksId),Book.firstauthor.in_(authorsId))).distinct()

    def FindAuthorsByBook(self, bookId):
        try:
            authors = []
            session = db.OpenSession()
            coAuthorBooks = session.query(CoAuthorBook).filter_by(book=bookId)
            if coAuthorBooks.count() == 0:
                book = session.query(Book).filter_by(id=bookId).first()
                author = session.query(Author).filter_by(id=book.firstauthor).first()
                return [author.fullname]
            for coAuthor in coAuthorBooks:
                author = session.query(Author).filter_by(id=coAuthor.author).first()
                authors.append(author.fullname)
            return authors
        except:
            logging.exception('')
            return []

    def post(self):
        try:
            requesterId = token.hasValidToken(request.headers.get('Authorization'))
            if not isinstance(requesterId, int):
                responseObject = {
                'status': 'forbidden',
                'message': 'Invalid Token'
                }
                return make_response(jsonify(responseObject)), 401

            if not token.IsAdmin(requesterId):
                responseObject = {
                'status': 'forbidden',
                'message': 'Your user does not have permission to perform this action.'
                }
                return make_response(jsonify(responseObject)), 401
            failedBooks = []
            books = request.get_json()['books']
            for book in books:
                if not self.UpsertBook(book):
                    failedBooks.append(book["title"])

            if len(failedBooks) == len(books):
                responseObject = {
                    'status': 'fail',
                    'message': 'Failed to create Books.'
                }
                return make_response(jsonify(responseObject)), 500
            elif len(failedBooks) > 0:
                responseObject = {
                    'status': 'Success',
                    'message': 'Some books could not be added to database.',
                    'failedbooks':failedBooks
                }
                return make_response(jsonify(responseObject)), 201

            responseObject = {
                'status': 'Success',
                'message': 'Books Added to Library'
            }
            return make_response(jsonify(responseObject)), 201
        except:
            logging.exception('')
            responseObject = {
                'status': 'fail',
                'message': 'Failed to create Books.'
            }
            return make_response(jsonify(responseObject)), 500
        


    def UpsertBook(self, book):
        try:
            session = db.OpenSession()
            existingBook = session.query(Book).filter_by(isbn=book["isbn"]).\
                        filter_by(title=book["title"]).first()
            if existingBook:
                existingBook.quantity += 1
                existingBook.availablequantity += 1
                session.commit()
                session.close()
                return True
            
            authorsId = self.UpsertAuthors(book["authors"])
            if not authorsId:
                session.close()
                return False

            newBook = Book(book["isbn"],book["title"],book["publisher"],authorsId[0],\
                1,1,0)
            session.add(newBook)
            session.commit()
            createdBook = session.query(Book).filter_by(isbn=book["isbn"]).\
                        filter_by(title=book["title"]).first()
            session.close()
            self.LinkCoAuthorsToBook(authorsId,createdBook)
        except:
            logging.exception('')
            return False

    def UpsertAuthors(self,authors):
        try:
            authorsId = []
            for author in authors:
                authorId = self.UpsertAuthor(author)
                if not authorId:
                    return None
                authorsId.append(authorId)
            return authorsId
        except:
            logging.exception('')
            return None
                

    def UpsertAuthor(self, author):
        try:
            session = db.OpenSession()
            existingAuthor = session.query(Author).filter_by(fullname=author).first()
            if existingAuthor:
                return existingAuthor.id
            newAuthor = Author(author,self.SetAuthorNickname(author), "Autor")
            session.add(newAuthor)
            session.commit()
            session.close()
            session = db.OpenSession()
            createdAuthor = session.query(Author).filter_by(fullname=author).first()
            session.close()
            return createdAuthor.id
        except:
            logging.exception('')
            return None


    def SetAuthorNickname(self,author):
        nickname = ""
        authorNames = author.split(" ")
        nickname = nickname.join([authorNames[len(authorNames)-1],","])
        for index in range(len(authorNames)-1):
            nickname = nickname+" "+authorNames[index][0]+"." 
        return nickname
    
    def LinkCoAuthorsToBook(self,authorsId,book):
        try:
            session = db.OpenSession()
            for authorId in authorsId:
                newLink = CoAuthorBook(book.id,authorId)
                session.add(newLink)
            session.commit()
            session.close()
            return True
        except:
            logging.exception('')
            return False
        

book_view =  BookView.as_view('book_view')

libraryManager.add_url_rule(
    '/book', 
    view_func=book_view, 
    methods=['GET', 'POST']
)
libraryManager.add_url_rule(
    '/book/<int:id>', 
    view_func=book_view, 
    methods=['GET']
)
libraryManager.add_url_rule(
    '/book/<field>&<value>', 
    view_func=book_view, 
    methods=['GET']
)
