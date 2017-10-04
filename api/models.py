from api import db
from datetime import datetime


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created = db.Column(db.DateTime, nullable=False)

    recipes = db.relationship("Recipe", backref="users", lazy=True)
    recipe_categories = db.relationship(
        "RecipeCategory", backref="users", lazy=True)

    def __init__(self, email, fname, lname, password, created=None):
        """ User initializer """
        self.email = email
        self.firstname = fname
        self.lastname = lname
        self.password = password
        if created:
            self.created = created
        else:
            self.created = datetime.utcnow()

    def __repr__(self):
        """ User object representation """
        return "<User {} {} {}>".format(self.id, self.firstname, self.lastname)


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    category_id = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(200))
    privacy = db.Column(db.Integer)
    favourite = db.Column(db.Integer)
    created = db.Column(db.DateTime)
    owner = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init__(self, name, description, category_id, owner_id, created=None):
        """ Recipe object initializer """
        self.name = name
        self.category_id = category_id
        self.description = description
        self.image = None
        self.privacy = 1
        self.favourite = 0
        if created:
            self.created = created
        else:
            self.created = datetime.utcnow()
        self.owner = owner_id

    def __repr__(self):
        """ Recipe object representation"""
        return "<Recipe {} {}>".format(self.id, self.name)


class RecipeCategory(db.Model):
    __tablename__ = "recipe_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey("users.id"))
    created = db.Column(db.DateTime)

    def __init__(self, name, owner, created):
        """ RecipeCategory object initializer """
        self.name = name
        self.owner = owner
        if created:
            self.created = created
        else:
            self.created = datetime.utcnow()

    def __repr__(self):
        """ RecipeCategory object representation """
        return "<RecipeCategory {} {}>".format(self.id, self.name)
