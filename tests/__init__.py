"""This is the tests module
The module has application specific tests
"""
# standard lib imports
import unittest
import json
from base64 import b64encode

# application specific imports
from api import app, db
from api.validator import Validate, ValidationError
from api.models import User, Recipe, RecipeCategory
from config import configs


class ApiBasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = app.test_client
        self.app.config.from_object(configs.get("testing"))
        db.create_all()

        # data to use when testing user registration and login
        self.expired_token = "ZXlKaGJHY2lPaUpJVXpJMU5pSXNJbWxoZENJNk1UVXhNVEE1TkRjMU1Dd2laWGh3SWpveE5URXhNRGs0TXpVd2ZRLmV5SnBaQ0k2TVgwLnQ1aEdhMmNON0RZU0VEYUxkSGljNHZXR1kzR1dzZF9wOEgyNTlka2o5YTQ"
        self.user_details1 = {"firstname": "Jjagwe", "lastname": "Dennis", "email": "dennisjjagwe@gmail.com",
                              "password": "password", "c_password": "password"}
        self.user_details2 = {"firstname": "King", "lastname": "Dennis", "email": "kingden@gmail.com",
                              "password": "mypassword", "c_password": "mypassword"}
        self.login_details1 = {
            "username": "dennisjjagwe@gmail.com", "password": "password"}
        self.login_details2 = {
            "username": "kingden@gmail.com", "password": "mypassword"}

        self.sample_categories = [{"cat_name": "Break Fast"}, {"cat_name": "Lunch and supper"},
                                  {"cat_name": "Evening Meals"}]
        self.sample_recipes = [
            {"name": "Banana Crumbs", "steps": "1.Peal Matooke 2.Cook 3.Eat", "ingredients": "Matooke, Tomatoes",
             "category": "1"},
            {"name": "Bread n Butter", "steps": "1.Open butter, 2.Open Bread 3.Spread butter on bread and eat",
             "ingredients": "Butter, Bread",
             "category": "1"}]

        self.kwargs = {"content_type": 'application/json'}

    def create_recipe_category(self, recipe_cat_details, login_token):
        self.kwargs["data"] = json.dumps(recipe_cat_details)
        self.kwargs["headers"] = {"x-access-token": login_token}
        return self.test_client().post("/yummy/api/v1.0/recipe_categories/", **self.kwargs)

    def create_recipe(self, recipe_details, login_token):
        self.kwargs["data"] = json.dumps(recipe_details)
        self.kwargs["headers"] = {"x-access-token": login_token}
        return self.test_client().post("/yummy/api/v1.0/recipes/", **self.kwargs)

    def get_token_from_response(self, response):
        return json.loads(response.data.decode()).get("token", None)

    def register_user(self, user_details):
        self.kwargs["data"] = json.dumps(user_details)
        return self.test_client().post("/yummy/api/v1.0/auth/register/", **self.kwargs)

    def login_user(self, user_details):
        credentials = f"{user_details['username']}:{user_details['password']}"
        headers = {
            "Authorization": f"Basic {b64encode(bytes(credentials,'utf-8')).decode('ascii')}"}
        return self.test_client().post("/yummy/api/v1.0/auth/login/", headers=headers)

    def register_and_login_user(self, user_reg=None, user_login=None):
        if not user_reg:
            user_reg = self.user_details1
        if not user_login:
            user_login = self.login_details1
        self.register_user(user_reg)
        return self.login_user(user_login)

    def get_response_on_change_password(self, current="wrongpassword", newpassword="newpassword",
                                        newpassword_again="newpassword"):
        # register user
        reg_response = self.register_user(self.user_details1)
        login_response = self.login_user(self.login_details1)
        token = self.get_token_from_response(login_response)

        # try changing user password when providing wrong current password
        self.kwargs["data"] = json.dumps(
            {"current_password": current, "new_password": newpassword, "new_password_again": newpassword_again})
        self.kwargs["headers"] = {"x-access-token": token}
        return self.test_client().patch("/yummy/api/v1.0/users/", **self.kwargs)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        self.kwargs = dict()


class AppTestCases(ApiBasicsTestCase):

    def test_app_is_not_null(self):
        self.assertTrue(self.app is not None)

    def test_app_is_using_test_database(self):
        self.assertTrue(self.app.config["TESTING"])
        self.assertTrue(self.app.config["DEBUG"])


if __name__ == "__main__":
    unittest.main()
