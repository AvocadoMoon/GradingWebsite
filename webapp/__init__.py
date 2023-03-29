from flask import Flask
from flask_wtf.csrf import CSRFProtect
from threading import Lock
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
studentPasswordsLock = Lock()
app.config['SECRET_KEY'] = b'\xf9c\xdc\xc6\x1bH\x8b\xd7\xa6\xd8\xc6\x0c*\xe8\x909'
csrf = CSRFProtect()
csrf.init_app(app)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024 #10 MB

cwd = os.getcwd()
sep = os.sep

from webapp import routes