""" this module creates an instance of our application """
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from config import CONFIGS as configs

app = Flask(__name__)
app.config.from_object(configs.get("development"))
db = SQLAlchemy(app)
cors = CORS(app)

# imports added here to avoid circular import errors
from api import models, auth, routes, errors
