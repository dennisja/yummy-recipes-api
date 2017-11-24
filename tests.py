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

    def test_app_is_not_null(self):
        self.assertTrue(self.app is not None)

    def test_app_is_using_test_database(self):
        self.assertTrue(self.app.config["TESTING"])
        self.assertTrue(self.app.config["DEBUG"])

    def test_user_registration_fails_if_no_data_is_sent(self):
        response = self.test_client().post("/yummy/api/v1.0/auth/register/")
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertTrue("Request not Understood" in response_data["errors"])

    def test_user_registration_fails_if_incomplete_data_is_sent(self):
        user_data = self.user_details1
        user_data.pop("password")
        self.kwargs.setdefault("data", json.dumps(user_data))
        response = self.test_client().post("/yummy/api/v1.0/auth/register/", **self.kwargs)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Validation failure: Check that you sent all the required data and try again",
                      str(response.data.decode("utf-8")))

    def test_user_registration_fails_if_invalid_data_is_sent(self):
        invalid_data = dict(self.user_details1)
        invalid_data["firstname"] = "g56"
        invalid_data["password"] = "pass"
        self.kwargs.setdefault("data", json.dumps(invalid_data))
        response = self.test_client().post("/yummy/api/v1.0/auth/register/", **self.kwargs)
        self.assertTrue(response.status_code, 422)
        self.assertIn("First Name must contain no digits",
                      response.data.decode())
        self.assertIn("Password must be a minimum of 8 characters",
                      response.data.decode())
        self.assertIn("Password must match Confirm Password",
                      response.data.decode())

    def test_user_can_register_if_correct_data_is_sent(self):
        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        # register a user
        response1 = self.test_client().post(
            "/yummy/api/v1.0/auth/register/", **self.kwargs)
        self.assertEqual(response1.status_code, 201)
        response_string = response1.data.decode()
        self.assertIn(
            "You have been successfully registered and you can now login", response_string)
        self.assertIn(self.user_details1["firstname"], response_string)
        self.assertIn(self.user_details1["lastname"], response_string)

    def test_cant_register_user_who_already_exists(self):
        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        # register a user
        response = self.test_client().post("/yummy/api/v1.0/auth/register/", **self.kwargs)
        self.assertEqual(response.status_code, 201)
        response_string = response.data.decode()
        self.assertIn(
            "You have been successfully registered and you can now login", response_string)
        self.assertIn(self.user_details1["firstname"], response_string)
        self.assertIn(self.user_details1["lastname"], response_string)
        # try registering the user again
        response1 = self.test_client().post(
            "/yummy/api/v1.0/auth/register/", **self.kwargs)
        response_string = response1.data.decode()
        self.assertEqual(response1.status_code, 422)
        self.assertIn(
            f"Email address \'{self.user_details1['email']}\' already in use", response_string)

    def test_user_cant_login_if_some_data_is_missing(self):
        # try logging in with no login data sent
        response = self.test_client().post("/yummy/api/v1.0/auth/login/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing login credentials", response.data.decode())
        # try logging in with only username
        headers = {
            "Authorization": f"Basic {b64encode(bytes('dennisjjagwe@gmail.com','utf-8')).decode('ascii')}"}
        response1 = self.test_client().post(
            "/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertEqual(response1.status_code, 400)
        self.assertIn("Missing login credentials", response1.data.decode())

    def test_user_cant_login_if_sent_data_has_validation_errors(self):
        headers = {
            "Authorization": f"Basic {b64encode(bytes('dennisjjagwe:myp','utf-8')).decode('ascii')}"}
        response1 = self.test_client().post(
            "/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertEqual(response1.status_code, 401)
        self.assertIn("Email is invalid", response1.data.decode())
        self.assertIn("Password must be a minimum of 8 characters",
                      response1.data.decode())
        self.assertIn("Invalid login credentials", str(response1.headers))

    def test_user_cant_login_if_he_has_not_yet_registered(self):
        credentials = f"{self.user_details1['email']}:{self.user_details1['password']}"
        headers = {
            "Authorization": f"Basic {b64encode(bytes(credentials,'utf-8')).decode('ascii')}"}
        response = self.test_client().post("/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertTrue(response.status_code, 404)
        self.assertIn(
            f"Email '{self.user_details1['email']}' is not yet registered", response.data.decode())

    def test_user_cant_login_if_he_supplies_a_wrong_password(self):
        credentials = f"{self.user_details1['email']}:wrongpassword"
        headers = {
            "Authorization": f"Basic {b64encode(bytes(credentials,'utf-8')).decode('ascii')}"}

        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        # register a user
        reg_response = self.test_client().post(
            "/yummy/api/v1.0/auth/register/", **self.kwargs)
        self.assertTrue(reg_response.status_code == 201)

        # login user with wrong password
        login_response = self.test_client().post(
            "/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertEqual(login_response.status_code, 401)
        self.assertIn("Invalid email and password combination",
                      login_response.data.decode())
        self.assertIn("Invalid email and password combination",
                      str(login_response.headers))

    def test_user_can_login_with_correct_credentials(self):
        credentials = f"{self.user_details1['email']}:{self.user_details1['password']}"
        headers = {
            "Authorization": f"Basic {b64encode(bytes(credentials,'utf-8')).decode('ascii')}"}

        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        # register a user
        reg_response = self.test_client().post(
            "/yummy/api/v1.0/auth/register/", **self.kwargs)
        self.assertTrue(reg_response.status_code == 201)

        # login user with wrong password
        login_response = self.test_client().post(
            "/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("Successfully logged in", login_response.data.decode())
        self.assertIn("token", login_response.data.decode())
        self.assertTrue(json.loads(login_response.data.decode())[
                        "token"] is not None)

    def test_user_cant_edit_details_with_expired_token(self):
        reg_response = self.register_user(self.user_details1)
        self.kwargs["data"] = json.dumps(
            {"firstname": "Jonah", "lastname": "Pat", "email": self.user_details2["email"]})
        self.kwargs["headers"] = {"x-access-token": self.expired_token}
        response = self.test_client().put("/yummy/api/v1.0/users/", **self.kwargs)
        self.assertEqual(response.status_code, 401)
        # self.assertIn("The token has expired", response.data.decode())

    def test_user_cant_edit_details_with_no_token(self):
        reg_response = self.register_user(self.user_details1)
        self.kwargs["data"] = json.dumps(
            {"firstname": "Jonah", "lastname": "Pat", "email": self.user_details2["email"]})
        response = self.test_client().put("/yummy/api/v1.0/users/", **self.kwargs)
        self.assertEqual(response.status_code, 401)
        self.assertIn("The access token is required", response.data.decode())

    def test_user_can_edit_his_own_details(self):
        # register two users
        reg_response = self.register_user(self.user_details1)
        login_response = self.login_user(self.login_details1)
        login_token = self.get_token_from_response(login_response)
        self.kwargs["data"] = json.dumps(
            {"firstname": "Jonah", "lastname": "Pat", "email": self.user_details2["email"]})
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().put("/yummy/api/v1.0/users/", **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertIn("All changes where applied successfully",
                      response.data.decode())

    def test_user_cant_change_email_to_existing_email_which_belongs_to_another_user(self):
        # register two users, login them and get their login tokens
        reg_responses = [self.register_user(
            self.user_details1), self.register_user(self.user_details2)]
        login_responses = [self.login_user(
            self.login_details1), self.login_user(self.login_details2)]
        login_tokens = [self.get_token_from_response(
            response) for response in login_responses]

        # try changing one of the user email to that of the other user
        self.kwargs["data"] = json.dumps(
            {"firstname": "Jonah", "lastname": "Pat", "email": self.user_details2["email"]})
        self.kwargs["headers"] = {"x-access-token": login_tokens[0]}

        response = self.test_client().put("/yummy/api/v1.0/users/", **self.kwargs)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            f"The email \'{self.user_details2['email']}\' is already in use", response.data.decode())

    def test_can_change_password_to_similar_password(self):
        response = self.get_response_on_change_password(current="password", newpassword="password",
                                                        newpassword_again="password")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Current Password must not be equal to New Password", response.data.decode())

    def test_user_cant_change_password_if_current_password_is_wrong(self):
        response = self.get_response_on_change_password()
        self.assertEqual(response.status_code, 403)
        self.assertIn("The current password supplied is wrong",
                      response.data.decode())

    def test_user_can_change_his_password(self):
        response = self.get_response_on_change_password(current="password")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Password Changed Successfully", response.data.decode())

    def test_retrieving_all_users(self):
        response = self.test_client().get("/yummy/api/v1.0/users/")
        self.assertEqual(response.status_code, 404)
        self.assertIn("No user found", response.data.decode())
        # register users
        reg_responses = [self.register_user(
            self.user_details1), self.register_user(self.user_details2)]
        response = self.test_client().get("/yummy/api/v1.0/users/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.data.decode())
        self.assertIn(self.user_details1["firstname"], response.data.decode())
        self.assertIn(self.user_details2["firstname"], response.data.decode())

    def test_retrieving_single_user_data(self):
        # try using an invalid public id
        response = self.test_client().get("/yummy/api/v1.0/users/1/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Request not Understood", response.data.decode())

        # register a user
        reg_response = self.register_user(self.user_details1)
        user_url = json.loads(reg_response.data.decode())["data"]["url"]

        # access registered user
        user_response = self.test_client().get(user_url)
        self.assertEqual(user_response.status_code, 200)
        self.assertIn(self.user_details1["email"], user_response.data.decode())

    def test_adding_recipe_category(self):
        # register and login a user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Successfully created recipe category",
                      response.data.decode())

    def test_cant_add_recipe_category_that_already_exists(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        again_response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        self.assertEqual(again_response.status_code, 400)
        self.assertIn("The Recipe Category you are trying to add already exists",
                      again_response.data.decode())

    def test_user_cant_add_category_if_invalid_data_is_sent(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        self.sample_categories[0]["cat_name"] = "h"
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Category Name must be a minimum of 3 characters", response.data.decode())

    def test_user_can_edit_recipe_category(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)

        # change category details
        self.sample_categories[0]["cat_name"] = "New Recipe Edited"
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn("Successfully edited recipe category",
                      edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 200)

    def test_cant_edit_category_that_belongs_to_another_user(self):
        """ Register and login two users """
        login_responses = [self.register_and_login_user(),
                           self.register_and_login_user(self.user_details2, self.login_details2)]
        login_tokens = [self.get_token_from_response(
            login_response) for login_response in login_responses]

        # create category using the first user
        self.kwargs["data"] = json.dumps({"cat_name": "This is new"})
        self.kwargs["headers"] = {"x-access-token": login_tokens[0]}
        response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        # try editing category details using the second user
        self.sample_categories[0]["cat_name"] = "New Recipe Edited"
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_tokens[1]}
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn("The recipe category you are trying to modify does not belong to you",
                      edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 403)

    def test_cant_edit_category_when_logged_out(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)

        # change category name to the same name
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs.pop("headers")
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn("The access token is required",
                      edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 401)

    def test_category_isnt_edited_if_current_and_new_category_names_are_similar(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)

        # change category name to the same name
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn(
            "The new recipe category name you are trying to use already exists", edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 400)

    def test_cant_edit_category_that_doesnot_exist(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)

        # change category details
        self.sample_categories[0]["cat_name"] = "New Recipe Edited"
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipe_categories/2", **self.kwargs)
        self.assertIn(
            "The recipe category you are trying to modify does not exist", edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 404)

    def test_user_can_delete_recipe_category(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)

        # delete the category
        self.kwargs.pop("data")
        delete_response = self.test_client().delete(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertEqual(delete_response.status_code, 200)
        self.assertIn("Recipe Category successfully deleted",
                      delete_response.data.decode())

    def test_cant_delete_a_category_that_belongs_to_another_user(self):
        """Register and login two users """
        login_responses = [self.register_and_login_user(),
                           self.register_and_login_user(self.user_details2, self.login_details2)]
        login_tokens = [self.get_token_from_response(
            login_response) for login_response in login_responses]

        # create category using the first user
        self.kwargs["data"] = json.dumps({"cat_name": "This is new"})
        self.kwargs["headers"] = {"x-access-token": login_tokens[0]}
        response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        # try deleting category  using the second user
        self.kwargs.pop("data")
        self.kwargs["headers"] = {"x-access-token": login_tokens[1]}
        delete_response = self.test_client().delete(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn("The recipe category you are trying to modify does not belong to you",
                      delete_response.data.decode())
        self.assertEqual(delete_response.status_code, 403)

    def test_user_cant_delete_a_category_that_doesnot_exist(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # delete a category that does not exist
        self.kwargs["headers"] = {"x-access-token": login_token}
        delete_response = self.test_client().delete(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertEqual(delete_response.status_code, 404)
        self.assertIn("The recipe category you are trying to modify does not exist",
                      delete_response.data.decode())

    def test_can_get_all_user_categories(self):
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create some recipe categories
        responses = [self.create_recipe_category(
            recipe_cat, login_token) for recipe_cat in self.sample_categories]

        # fetch all the categories
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().get(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Recipe Categories exists", response.data.decode())

    def test_can_get_all_recipes_in_a_category(self):
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create a recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)

        # add recipes to the recipe category
        add_recipe_responses = [self.create_recipe(
            recipe, login_token) for recipe in self.sample_recipes]
        # fetch the recipes is the category
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().get(
            "/yummy/api/v1.0/recipe_categories/1/recipes/", **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Category exists", response.data.decode())
        self.assertIn(self.sample_recipes[0]["steps"], response.data.decode())

    def test_can_get_recipe_category(self):
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create a recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        response = self.test_client().get("/yummy/api/v1.0/recipe_categories/1",
                                          headers={"x-access-token": login_token})
        self.assertIn("Recipe category exists", response.data.decode())
        self.assertIn(
            self.sample_categories[0]["cat_name"], response.data.decode())
        self.assertEqual(response.status_code, 200)

    def test_can_add_recipe(self):
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # add recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # add recipe to a category
        response = self.create_recipe(self.sample_recipes[0], login_token)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Successfully added recipe", response.data.decode())
        self.assertIn(self.sample_recipes[0]["steps"], response.data.decode())
        self.assertIn(
            self.sample_categories[0]["cat_name"], response.data.decode())

    def test_cant_add_recipe_in_a_category_that_doesnot_exist(self):
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # add recipe to a category that does not exist
        response = self.create_recipe(self.sample_recipes[0], login_token)
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            "Trying to add a recipe to a category that does not exist", response.data.decode())

    def test_cant_add_recipe_to_a_category_that_belongs_to_another_user(self):
        # register and login two users
        login_responses = [self.register_and_login_user(),
                           self.register_and_login_user(self.user_details2, self.login_details2)]
        login_tokens = [self.get_token_from_response(
            login_response) for login_response in login_responses]

        # create a recipe category using 1 user
        self.create_recipe_category(self.sample_categories[0], login_tokens[0])
        # add recipe to the same category using another user
        response = self.create_recipe(self.sample_recipes[0], login_tokens[1])
        # test if addition fails
        self.assertEqual(response.status_code, 403)
        self.assertIn(
            "Trying to add a recipe to a category that does not belong to you", response.data.decode())

    def test_cant_add_recipe_in_a_category_where_another_recipe_with_same_name_exists(self):
        # register and login a user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create a recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # add two recipes in the same category with the same name
        response_one = self.create_recipe(self.sample_recipes[0], login_token)
        response_two = self.create_recipe(self.sample_recipes[0], login_token)
        # test if this fails
        self.assertEqual(response_two.status_code, 400)
        self.assertIn("A recipe with the same name, by the same user already exists in the same category",
                      response_two.data.decode())

    def test_cant_add_recipe_when_invalid_data_is_supplied(self):
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # try adding recipe with data that violates validation rules
        self.sample_recipes[0]["name"] = "p"
        self.sample_recipes[0]["steps"] = "no"
        response = self.create_recipe(self.sample_recipes[0], login_token)
        # test if the addition fails
        self.assertEqual(response.status_code, 400)
        self.assertIn("Name must be a minimum of 3 characters",
                      response.data.decode())
        self.assertIn("Steps must be a minimum of 10 characters",
                      response.data.decode())

    def test_can_edit_recipe(self):
        # login and register user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # create recipe
        self.create_recipe(self.sample_recipes[0], login_token)
        # edit the recipe
        self.kwargs["data"] = json.dumps(self.sample_recipes[1])
        self.kwargs["headers"] = {"x-access-token": login_token}
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipes/1", **self.kwargs)
        # test if recipe is edited
        self.assertEqual(edit_response.status_code, 200)
        self.assertIn("Successfully edited recipe",
                      edit_response.data.decode())
        self.assertIn(self.sample_recipes[1]
                      ["steps"], edit_response.data.decode())

    def test_can_change_recipe_category_to_a_category_that_doesnot_exist(self):
        """ Ensures that a user cannot change recipe category to an id of the recipe category that doesnot exist"""
        # login and register user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # create recipe
        self.create_recipe(self.sample_recipes[0], login_token)
        # try to edit recipe and use a category that does not exist
        self.sample_recipes[1]["category"] = 4
        self.kwargs["data"] = json.dumps(self.sample_recipes[1])
        self.kwargs["headers"] = {"x-access-token": login_token}
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipes/1", **self.kwargs)
        # test if editing fails
        self.assertEqual(edit_response.status_code, 404)
        self.assertIn(
            "Trying to move a recipe to a category that does not exist", edit_response.data.decode())

    def test_can_edit_recipe_category_to_a_category_that_doesnot_belong_to_you(self):
        """ Ensures that user cannot change recipe category to a category id that belongs to another user"""
        # register and login two users
        login_responses = [self.register_and_login_user(),
                           self.register_and_login_user(self.user_details2, self.login_details2)]
        login_tokens = [self.get_token_from_response(
            login_response) for login_response in login_responses]

        # create two recipe categories with different users
        categories = [self.create_recipe_category(self.sample_categories[0], login_tokens[0]),
                      self.create_recipe_category(self.sample_categories[1], login_tokens[1])]
        # create recipe with one user
        recipe_response = self.create_recipe(
            self.sample_recipes[0], login_tokens[0])
        # edit recipe specifying category of the other user
        self.kwargs["headers"] = {"x-access-token": login_tokens[0]}
        self.sample_recipes[1]["category"] = 2
        self.kwargs["data"] = json.dumps(self.sample_recipes[1])
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipes/1", **self.kwargs)
        # test whether editing fails
        self.assertTrue(edit_response.status_code, 400)
        self.assertIn(
            "Trying to move a recipe to a category that does not belong to you", edit_response.data.decode())

    def test_can_only_edit_recipe_that_belongs_to_you(self):
        # register and login two users
        login_responses = [self.register_and_login_user(),
                           self.register_and_login_user(self.user_details2, self.login_details2)]
        login_tokens = [self.get_token_from_response(
            login_response) for login_response in login_responses]
        # create a recipe category using 1 user
        self.create_recipe_category(self.sample_categories[0], login_tokens[0])
        # create recipe in that category using the same user
        self.create_recipe(self.sample_recipes[0], login_tokens[0])
        # try editing the recipe using the other user
        self.kwargs["headers"] = {"x-access-token": login_tokens[1]}
        self.kwargs["data"] = json.dumps(self.sample_recipes[1])
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipes/1", **self.kwargs)
        # test whether addition fails
        self.assertTrue(edit_response.status_code, 400)
        self.assertIn(
            "You are trying to modify a recipe that does not belong to you", edit_response.data.decode())

    def test_can_only_edit_recipe_that_exists(self):
        # register and login a user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # try editing a recipe in thet category that doesnot exist
        self.kwargs["headers"] = {"x-access-token": login_token}
        self.kwargs["data"] = json.dumps(self.sample_recipes[0])
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipes/1", **self.kwargs)
        # test if editing fails
        self.assertTrue(edit_response.status_code, 200)
        self.assertIn("Trying to access a recipe that does not exist",
                      edit_response.data.decode())

    def test_can_publish_recipe(self):
        # register and login a user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # create a recipe in the category
        self.create_recipe(self.sample_recipes[0], login_token)
        # publish the recipe
        publish_response = self.test_client().patch("/yummy/api/v1.0/recipes/1",
                                                    headers={"x-access-token": login_token})
        # test whether recipe is published
        self.assertTrue(publish_response.status_code, 200)
        self.assertIn("Published recipe", publish_response.data.decode())

    def test_can_publish_another_users_recipe(self):
        """ Ensures that a user cannot publish another users recipe"""
        # login two users
        login_responses = [self.register_and_login_user(),
                           self.register_and_login_user(self.user_details2, self.login_details2)]
        login_tokens = [self.get_token_from_response(
            login_response) for login_response in login_responses]

        # create category using one user
        self.create_recipe_category(self.sample_categories[0], login_tokens[0])
        # add recipe to the same category using the same user
        self.create_recipe(self.sample_recipes[0], login_tokens[0])
        # try publishing recipe using the other user
        publish_response = self.test_client().patch("/yummy/api/v1.0/recipes/1",
                                                    headers={"x-access-token": login_tokens[1]})
        # test if publishing fails
        self.assertTrue(publish_response.status_code, 400)
        self.assertIn("You are trying to modify a recipe that does not belong to you",
                      publish_response.data.decode())

    def test_can_delete_recipe(self):
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create a recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # create a recipe
        self.create_recipe(self.sample_recipes[0], login_token)
        # delete the recipe
        delete_response = self.test_client().delete("/yummy/api/v1.0/recipes/1",
                                                    headers={"x-access-token": login_token})
        # test to see whether deletion succeeds
        self.assertTrue(delete_response.status_code, 200)
        self.assertIn("Successfully deleted a recipe",
                      delete_response.data.decode())

    def test_can_only_delete_own_recipes(self):
        """ Ensure that a user can only delete his own recipes"""
        # register and login two users
        login_responses = [self.register_and_login_user(),
                           self.register_and_login_user(self.user_details2, self.login_details2)]
        login_tokens = [self.get_token_from_response(
            login_response) for login_response in login_responses]
        # create a recipe category using 1 user
        self.create_recipe_category(self.sample_categories[0], login_tokens[0])
        # create recipe in that category using the same user
        self.create_recipe(self.sample_recipes[0], login_tokens[0])
        # try deleting that recipe using the other user
        delete_response = self.test_client().delete("/yummy/api/v1.0/recipes/1",
                                                    headers={"x-access-token": login_tokens[1]})
        # test if deletion fails
        self.assertEqual(delete_response.status_code, 403)
        self.assertIn("You are trying to modify a recipe that does not belong to you",
                      delete_response.data.decode())

    def test_can_get_all_user_recipes(self):
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create a recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # create recipes in that category
        recipe_responses = [self.create_recipe(recipe, login_token) for recipe in self.sample_recipes if
                            recipe["category"] == "1"]
        # access the recipes in that category
        response = self.test_client().get("/yummy/api/v1.0/recipes/",
                                          headers={"x-access-token": login_token})
        # test to see if your recipes are fetched
        self.assertTrue(response.status_code == 200)
        self.assertIn("recipes", response.data.decode())
        self.assertIn(self.sample_recipes[0]["steps"], response.data.decode())
        self.assertIn(self.sample_recipes[0]["name"], response.data.decode())
        self.assertIn(self.sample_recipes[1]["steps"], response.data.decode())

    def test_can_get_single_recipe(self):
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create a recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # create a recipe
        self.create_recipe(self.sample_recipes[0], login_token)
        # access the recipe
        response = self.test_client().get("/yummy/api/v1.0/recipes/1",
                                          headers={"x-access-token": login_token})
        # test if recipe can be accessed
        self.assertEqual(response.status_code, 200)
        self.assertIn("Recipe exists", response.data.decode())
        self.assertIn(self.sample_recipes[0]["steps"], response.data.decode())

    def create_recipe(self, recipe_details, login_token):
        self.kwargs["data"] = json.dumps(recipe_details)
        self.kwargs["headers"] = {"x-access-token": login_token}
        return self.test_client().post("/yummy/api/v1.0/recipes/", **self.kwargs)

    def test_can_search_recipes_users_and_categories(self):
        # login and register two users
        login_responses = [self.register_and_login_user(),
                           self.register_and_login_user(self.user_details2, self.login_details2)]
        login_tokens = [self.get_token_from_response(
            login_response) for login_response in login_responses]
        # create some recipe categories
        category_reponses = [self.create_recipe_category(
            cat, login_tokens[0]) for cat in self.sample_categories]
        # create some recipes
        recipe_responses = [self.create_recipe(
            recipe, login_tokens[0]) for recipe in self.sample_recipes]

        # test to see if search is successful
        response = self.test_client().get("/yummy/api/v1.0/search?q=a&page=1")
        self.assertEqual(response.status_code, 200)
        self.assertIn("recipes", response.data.decode())
        self.assertIn("recipe_categories", response.data.decode())
        self.assertIn("users", response.data.decode())
        self.assertIn(self.user_details1["email"], response.data.decode())
        self.assertIn(
            self.sample_categories[0]["cat_name"], response.data.decode())
        self.assertIn(self.sample_recipes[0]["name"], response.data.decode())

    def test_search_fails_when_q_param_is_missing(self):
        # login and register two users
        login_responses = [self.register_and_login_user(),
                           self.register_and_login_user(self.user_details2, self.login_details2)]
        login_tokens = [self.get_token_from_response(
            login_response) for login_response in login_responses]
        # create some recipe categories
        category_reponses = [self.create_recipe_category(
            cat, login_tokens[0]) for cat in self.sample_categories]
        # create some recipes
        recipe_responses = [self.create_recipe(
            recipe, login_tokens[0]) for recipe in self.sample_recipes]

        # test to see if search is successful
        response = self.test_client().get("/yummy/api/v1.0/search?page=1")
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Check that you have supplied the search term and try again", response.data.decode())

    def test_search_fails_when_all_get_param_are_missing(self):
        # login and register two users
        login_responses = [self.register_and_login_user(),
                           self.register_and_login_user(self.user_details2, self.login_details2)]
        login_tokens = [self.get_token_from_response(
            login_response) for login_response in login_responses]
        # create some recipe categories
        category_reponses = [self.create_recipe_category(
            cat, login_tokens[0]) for cat in self.sample_categories]
        # create some recipes
        recipe_responses = [self.create_recipe(
            recipe, login_tokens[0]) for recipe in self.sample_recipes]

        # test to see if search is successful
        response = self.test_client().get("/yummy/api/v1.0/search")
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Check that you have supplied all the required data and try again", response.data.decode())

    def create_recipe_category(self, recipe_cat_details, login_token):
        self.kwargs["data"] = json.dumps(recipe_cat_details)
        self.kwargs["headers"] = {"x-access-token": login_token}
        return self.test_client().post("/yummy/api/v1.0/recipe_categories/", **self.kwargs)

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


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User("dennisjjagwe@gmail.com",
                         "jjagwe", "dennis", "mypassword")

    def test_user_has_no_id_before_addition_to_database(self):
        self.assertFalse(self.user.id is not None)
        self.assertTrue(self.user.id is None)

    def test_verify_password(self):
        self.assertTrue(self.user.verify_password("mypassword"))
        self.assertFalse(self.user.verify_password("otherpassword"))

    def test_set_password(self):
        self.user.set_password("new_password")
        self.assertTrue(self.user.verify_password("new_password"))
        self.assertFalse(self.user.verify_password("mypassword"))

    def test_stored_passwords_are_random_if_password_strings_are_similar(self):
        user1 = User("dennisj@gmail.com", "jjagwe", "denni", "password")
        user2 = User("dennisj@gmail.com", "king", "dennis", "password")
        self.assertTrue(user1.password != user2.password)
        self.assertFalse(user2.password == user1.password)


class ValidatorTestCases(unittest.TestCase):
    def setUp(self):
        self.validator = Validate()

    def test_empty_required_submitted_value(self):
        form_data = {"lastname": ""}
        rules = {"lastname": {
            "required": True
        }}
        self.assertTrue(self.validator.validate_data(form_data, rules))

    def test_no_number_in_submitted_value(self):
        form_data = {"lastname": "d56"}
        rules = {"lastname": {
            "no_number": True
        }}
        self.assertTrue(self.validator.validate_data(form_data, rules))

    def test_min_length_of_submitted_value(self):
        form_data = {"lastname": "den"}
        rules = {"lastname": {
            "min": 6
        }}
        self.assertTrue(self.validator.validate_data(form_data, rules))

    def test_max_length_of_submitted_value(self):
        form_data = {"lastname": "denhhhhh"}
        rules = {"lastname": {
            "max": 6
        }}
        self.assertTrue(self.validator.validate_data(form_data, rules))

    def test_invalid_key_from_in_user_data(self):
        form_data = {
            "absent_key": ""
        }
        rules = {"absent_key": {
            "required": True
        }}
        self.assertRaises(KeyError, self.validator.validate_data,
                          source=form_data, items=rules)


if __name__ == "__main__":
    unittest.main()
