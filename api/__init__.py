from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:mypassword@127.0.0.1/yummy_api"
db = SQLAlchemy(app)

