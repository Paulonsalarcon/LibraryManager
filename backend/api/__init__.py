#!flask/bin/python
import pathlib, sys
currentPath = pathlib.Path(__file__).parent.absolute()
parentdir = currentPath.parent.absolute()
sys.path.insert(0,parentdir) 

from flask import Flask, jsonify, abort, make_response
from flask_bcrypt import Bcrypt
from database import LibraryManagerDB

app = Flask(__name__)

bcrypt = Bcrypt(app)
db = LibraryManagerDB()
db.Connect()

from .token import *
from .UsersViews import *
from .AuthenticationViews import *
from .LibraryManagementViews import libraryManager

app.register_blueprint(libraryManager)