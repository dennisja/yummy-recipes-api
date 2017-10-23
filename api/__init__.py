from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:mypassword@127.0.0.1:5432/yummy_recipes"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "THhdtgUhhkdldyrhfkfu8369kslo09wjjw"
db = SQLAlchemy(app)


from api import models, routes


