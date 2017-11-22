from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from config import configs

app = Flask(__name__)
app.config.from_object(configs.get("production"))
db = SQLAlchemy(app)
cors = CORS(app)


from api import models, routes


