from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import configs

app = Flask(__name__)
app.config.from_object(configs.get("production"))
db = SQLAlchemy(app)


from api import models, routes


