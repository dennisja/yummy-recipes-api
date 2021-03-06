"""This is the models module
It has models to be used in the application
"""
# standard lib modules
from datetime import datetime

# third party modules
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash

# application specific modules
from api.helpers import Secure, format_data
from api import db


class UserNotFoundError(Exception):
    """ Thrown when trying a user who doesnot exist """
    pass


class User(db.Model):
    """ Contains information about the user  """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile = db.Column(db.String(15), unique=True, nullable=True)
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    recipes = db.relationship("Recipe", backref="creator", lazy="dynamic")
    recipe_categories = db.relationship(
        "RecipeCategory", backref="creator", lazy="dynamic")

    def __init__(self, email, fname, lname, password, mobile=None):
        """ User initializer """
        self.email = email
        self.firstname = fname
        self.lastname = lname
        self.set_password(password)
        self.mobile = mobile

    def set_password(self, password):
        """ Sets user password to a new password"""
        self.password = generate_password_hash(
            password, method="pbkdf2:sha256")

    def verify_password(self, password):
        """
        Checks if user supplied a correct password
        :param password: Password user has provided
        :return: True if password is correct false otherwise
        """
        return check_password_hash(self.password, password)

    def save_user(self):
        """ saves the current user to the database"""
        db.session.add(self)
        db.session.commit()

    @property
    def user_details(self):
        """ Returns the user json representation """
        user_details = {
            "id":
            self.id,
            "firstname":
            self.firstname,
            "lastname":
            self.lastname,
            "email":
            self.email,
            "mobile":
            self.mobile,
            "url":
            url_for(
                "get_user", id=self.id, _external=True)
        }
        return user_details

    def __repr__(self):
        """ User object representation """
        return f"<User {self.id} {self.firstname} {self.lastname}>"


class Recipe(db.Model):
    """ Contains information about a recipe """
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    steps = db.Column(db.String(1000))
    ingredients = db.Column(db.String(500))
    category_id = db.Column(
        db.Integer, db.ForeignKey("recipe_categories.id"), nullable=False)
    image = db.Column(db.String(200))
    privacy = db.Column(db.Integer, default=1)
    favourite = db.Column(db.Integer, default=0)
    created = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp())
    edited = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    owner = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __init__(self, name, steps, ingredients, category_id, owner_id):
        """ Recipe object initializer """
        self.name = name
        self.steps = steps
        self.ingredients = ingredients
        self.category_id = category_id
        self.owner = owner_id
        self.image = None

    @property
    def recipe_details(self):
        """ Contains information about a recipe """
        return {
            "id": self.id,
            "name": self.name,
            "steps": self.steps,
            "ingredients": self.ingredients,
            "category": self.recipe_category.recipe_cat_details,
            "image": self.image,
            "privacy": self.privacy,
            "favourite": self.favourite,
            "created": self.created,
            "edited": self.edited,
            "url": url_for("get_recipe", recipe_id=self.id, _external=True)
        }

    def save_recipe(self):
        """ Saves a recipe """
        db.session.add(self)
        db.session.commit()

    def delete_recipe(self):
        """ Deletes a recipe """
        db.session.delete(self)
        db.session.commit()

    def edit_recipe(self, recipe_data):
        """ Edits a recipe """
        self.name = format_data(recipe_data.get("name", self.name))
        self.steps = recipe_data.get("steps", self.steps)
        self.ingredients = recipe_data.get("ingredients", self.ingredients)
        self.category_id = recipe_data.get("category", self.category_id)
        db.session.commit()

    def __repr__(self):
        """ Recipe object representation"""
        return f"<Recipe {self.id} {self.name}>"


class RecipeCategory(db.Model):
    """ Has information about a recipe category """
    __tablename__ = "recipe_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp())
    edited = db.Column(
        db.DateTime,
        nullable=False,
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    recipes = db.relationship(
        "Recipe",
        backref="recipe_category",
        lazy="dynamic",
        cascade="all, delete-orphan")

    def __init__(self, name, owner):
        """ RecipeCategory object initializer """
        self.name = name
        self.owner = owner

    def save_recipe_cat(self):
        """ Saves a recipe category """
        db.session.add(self)
        db.session.commit()

    def delete_recipe_cat(self):
        """ Deletes a recipe category """
        db.session.delete(self)
        db.session.commit()

    @property
    def recipe_cat_details(self):
        """ Returns a dictionary containing details about a recipe category """
        return {
            "id":
            self.id,
            "name":
            self.name,
            "owner_details":
            self.creator.user_details,
            "created":
            self.created,
            "edited":
            self.edited,
            "url":
            url_for(
                "get_recipe_category", category_id=self.id, _external=True)
        }

    def __repr__(self):
        """ RecipeCategory object representation """
        return f"<RecipeCategory {self.id} {self.name}>"
