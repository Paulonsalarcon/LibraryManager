from flask import Blueprint

libraryManager = Blueprint('libraryManager', __name__)
 
@libraryManager.route('/')
@libraryManager.route('/home')
def home():
    return "Welcome to the Library Manager Home."