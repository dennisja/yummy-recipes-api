from api import db
from datetime import datetime
from api.validator import Validate
from flask import url_for

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(15), unique=True, nullable=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime, nullable=False)

    recipes = db.relationship("Recipe", backref="users", lazy="dynamic")
    recipe_categories = db.relationship(
        "RecipeCategory", backref="users", lazy="dynamic")

    def __init__(self, email, fname, lname, password,mobile=None, created=None):
        """ User initializer """
        self.email = email
        self.firstname = fname
        self.lastname = lname
        self.password = password,
        self.mobile = mobile
        if created:
            self.created = created
        else:
            self.created = datetime.utcnow()

    def save_user(self):
        """ saves the current user to the database"""
        db.session.add(self)
        db.session.commit()

    @property
    def user_details(self):
        """ Returns the user json representation """
        user_details = {
            "id":self.id,
            "firstname":self.firstname,
            "lastname":self.lastname,
            "email":self.email,
            "mobile":self.mobile,
            "url": url_for("get_user", id=self.id, _external=True)
        }
        return user_details


    @staticmethod
    def validate_user(user_details):
        """
        Validates the submitted user data
        :param user_details: The user details from the request
        :return: A list of validation errors spotted in the submitted user data
        """
        data_validator = Validate()
        validation_errors = data_validator.validate_data(user_details, {
            "firstname": {
                "required": True,
                "max": 20,
                "no_number": True
            },
            "lastname": {
                "required": True,
                "max": 20,
                "no_number": True
            },
            "email": {
                "required": True,
                "email": True,
                "min": 8,
                "max": 100
            },
            "password": {
                "required": True,
                "min": 8,
                "max": 20
            },
            "c_password": {
                "matches": "password"
            }
        })

        return validation_errors


    def __repr__(self):
        """ User object representation """
        return "<User {} {} {}>".format(self.id, self.firstname, self.lastname)


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    category_id = db.Column(db.Integer, db.ForeignKey("recipe_categories.id"), nullable=False)
    image = db.Column(db.String(200))
    privacy = db.Column(db.Integer)
    favourite = db.Column(db.Integer)
    created = db.Column(db.DateTime)
    edited = db.Column(db.DateTime)
    owner = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init__(self, name, description, category_id, owner_id, created=None, edited=None):
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

        if edited:
            self.edited = edited

    def __repr__(self):
        """ Recipe object representation"""
        return "<Recipe {} {}>".format(self.id, self.name)


class RecipeCategory(db.Model):
    __tablename__ = "recipe_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    owner = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    edited = db.Column(db.DateTime, nullable=True)

    recipes = db.relationship(
        "Recipe", backref="recipe_category", lazy="dynamic")

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
