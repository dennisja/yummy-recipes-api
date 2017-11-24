from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from config import configs

app = Flask(__name__)
app.config.from_object(configs.get("development"))
db = SQLAlchemy(app)
cors = CORS(app)

# imports added here to avoid cyclic imports
from api import models, auth, routes, errors
