from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import configs
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(configs.get("production"))
db = SQLAlchemy(app)
cors = CORS(app)


from api import models, routes


