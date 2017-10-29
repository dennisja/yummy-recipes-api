from api import app, db
from api.models import User, Recipe, RecipeCategory
import unittest
import json
from base64 import b64encode


class ApiBasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_client = app.test_client
        self.app.config[
            "SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:mypassword@127.0.0.1:5432/test_yummy_recipes"
        db.create_all()

        # data to use when testing user registration and login
        self.user_details1 = {"firstname": "Jjagwe", "lastname": "Dennis", "email": "dennisjjagwe@gmail.com",
                              "password": "password", "c_password": "password"}
        self.user_details2 = {"firstname": "King", "lastname": "Dennis", "email": "kingden@gmail.com",
                              "password": "mypassword", "c_password": "mypassword"}
        self.login_details1 = {"username": "dennisjjagwe@gmail.com", "password": "password"}
        self.login_details2 = {"username": "kingden@gmail.com", "password": "mypassword"}

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
        self.assertEqual(self.app.config["SQLALCHEMY_DATABASE_URI"],
                         "postgresql://postgres:mypassword@127.0.0.1:5432/test_yummy_recipes")

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
        self.assertIn("First Name must contain no digits", response.data.decode())
        self.assertIn("Password must be a minimum of 8 characters", response.data.decode())
        self.assertIn("Password must match Confirm Password", response.data.decode())

    def test_user_can_register_if_correct_data_is_sent(self):
        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        # register a user
        response1 = self.test_client().post("/yummy/api/v1.0/auth/register/", **self.kwargs)
        self.assertEqual(response1.status_code, 201)
        response_string = response1.data.decode()
        self.assertIn("You have been successfully registered and you can now login", response_string)
        self.assertIn(self.user_details1["firstname"], response_string)
        self.assertIn(self.user_details1["lastname"], response_string)

    def test_cant_register_user_who_already_exists(self):
        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        # register a user
        response = self.test_client().post("/yummy/api/v1.0/auth/register/", **self.kwargs)
        self.assertEqual(response.status_code, 201)
        response_string = response.data.decode()
        self.assertIn("You have been successfully registered and you can now login", response_string)
        self.assertIn(self.user_details1["firstname"], response_string)
        self.assertIn(self.user_details1["lastname"], response_string)
        # try registering the user again
        response1 = self.test_client().post("/yummy/api/v1.0/auth/register/", **self.kwargs)
        response_string = response1.data.decode()
        self.assertEqual(response1.status_code, 422)
        self.assertIn(f"Email address \'{self.user_details1['email']}\' already in use", response_string)

    def test_user_cant_login_if_some_data_is_missing(self):
        # try logging in with no login data sent
        response = self.test_client().post("/yummy/api/v1.0/auth/login/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing login credentials", response.data.decode())
        # try logging in with only username
        headers = {"Authorization": f"Basic {b64encode(bytes('dennisjjagwe@gmail.com','utf-8')).decode('ascii')}"}
        response1 = self.test_client().post("/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertEqual(response1.status_code, 400)
        self.assertIn("Missing login credentials", response1.data.decode())

    def test_user_cant_login_if_sent_data_has_validation_errors(self):
        headers = {"Authorization": f"Basic {b64encode(bytes('dennisjjagwe:myp','utf-8')).decode('ascii')}"}
        response1 = self.test_client().post("/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertEqual(response1.status_code, 401)
        self.assertIn("Email is invalid", response1.data.decode())
        self.assertIn("Password must be a minimum of 8 characters", response1.data.decode())
        self.assertIn("Invalid login credentials", str(response1.headers))

    def test_user_cant_login_if_he_has_not_yet_registered(self):
        credentials = f"{self.user_details1['email']}:{self.user_details1['password']}"
        headers = {"Authorization": f"Basic {b64encode(bytes(credentials,'utf-8')).decode('ascii')}"}
        response = self.test_client().post("/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertTrue(response.status_code, 404)
        self.assertIn(f"Email '{self.user_details1['email']}' is not yet registered", response.data.decode())

    def test_user_cant_login_if_he_supplies_a_wrong_password(self):
        credentials = f"{self.user_details1['email']}:wrongpassword"
        headers = {"Authorization": f"Basic {b64encode(bytes(credentials,'utf-8')).decode('ascii')}"}

        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        # register a user
        reg_response = self.test_client().post("/yummy/api/v1.0/auth/register/", **self.kwargs)
        self.assertTrue(reg_response.status_code == 201)

        # login user with wrong password
        login_response = self.test_client().post("/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertEqual(login_response.status_code, 401)
        self.assertIn("Invalid email and password combination", login_response.data.decode())
        self.assertIn("Invalid email and password combination", str(login_response.headers))

    def test_user_can_login_with_correct_credentials(self):
        credentials = f"{self.user_details1['email']}:{self.user_details1['password']}"
        headers = {"Authorization": f"Basic {b64encode(bytes(credentials,'utf-8')).decode('ascii')}"}

        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        # register a user
        reg_response = self.test_client().post("/yummy/api/v1.0/auth/register/", **self.kwargs)
        self.assertTrue(reg_response.status_code == 201)

        # login user with wrong password
        login_response = self.test_client().post("/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("Successfully logged in", login_response.data.decode())
        self.assertIn("token", login_response.data.decode())
        self.assertTrue(json.loads(login_response.data.decode())["token"] is not None)

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
        self.assertIn("All changes where applied successfully", response.data.decode())

    def test_user_cant_change_email_to_existing_email_which_belongs_to_another_user(self):
        # register two users, login them and get their login tokens
        reg_responses = [self.register_user(self.user_details1), self.register_user(self.user_details2)]
        login_responses = [self.login_user(self.login_details1), self.login_user(self.login_details2)]
        login_tokens = [self.get_token_from_response(response) for response in login_responses]

        # try changing one of the user email to that of the other user
        self.kwargs["data"] = json.dumps(
            {"firstname": "Jonah", "lastname": "Pat", "email": self.user_details2["email"]})
        self.kwargs["headers"] = {"x-access-token": login_tokens[0]}

        response = self.test_client().put("/yummy/api/v1.0/users/", **self.kwargs)
        self.assertEqual(response.status_code, 400)
        self.assertIn(f"The email \'{self.user_details2['email']}\' is already in use", response.data.decode())

    def test_current_and_new_passwords_must_be_different(self):
        # response = self.get_response_on_change_password(current="password", newpassword="password",
        #                                                 newpassword_again="password")
        # self.assertEqual(response.status_code, 400)
        # self.assertIn("Current Password must not be equal to New Password", response.data.decode())
        pass

    def test_user_cant_change_password_if_current_password_is_wrong(self):
        response = self.get_response_on_change_password()
        self.assertEqual(response.status_code, 403)
        self.assertIn("The current password supplied is wrong", response.data.decode())

    def test_user_can_change_his_password(self):
        response = self.get_response_on_change_password(current="password")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Password Changed Successfully", response.data.decode())

    def test_retrieving_all_users(self):
        response = self.test_client().get("/yummy/api/v1.0/users/")
        self.assertEqual(response.status_code, 404)
        self.assertIn("No user found", response.data.decode())
        # register users
        reg_responses = [self.register_user(self.user_details1), self.register_user(self.user_details2)]
        response = self.test_client().get("/yummy/api/v1.0/users/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.data.decode())
        self.assertIn(self.user_details1["firstname"], response.data.decode())
        self.assertIn(self.user_details2["firstname"], response.data.decode())

    def test_retrieving_single_user_data(self):
        # try using an invalid public id
        response = self.test_client().get("/yummy/api/v1.0/users/1/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Request not understood", response.data.decode())

        # register a user
        reg_response = self.register_user(self.user_details1)
        user_url = json.loads(reg_response.data.decode())["data"]["url"]

        # access registered user
        user_response = self.test_client().get(user_url)
        self.assertEqual(user_response.status_code, 200)
        self.assertIn(self.user_details1["email"], user_response.data.decode())

    def register_and_login_user(self, user_reg=None, user_login=None):
        if not user_reg:
            user_reg = self.user_details1
        if not user_login:
            user_login = self.login_details1
        self.register_user(user_reg)
        return self.login_user(user_login)

    def test_adding_recipe_category(self):
        # register and login a user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post("/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Successfully created recipe category", response.data.decode())

    def test_cant_add_recipe_category_that_already_exists(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post("/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        again_response = self.test_client().post("/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        self.assertEqual(again_response.status_code, 400)
        self.assertIn("The Recipe Category you are trying to add already exists", again_response.data.decode())

    def test_user_cant_add_category_if_invalid_data_is_sent(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        self.sample_categories[0]["cat_name"] = "h"
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post("/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Category Name must be a minimum of 3 characters", response.data.decode())

    def test_user_can_edit_recipe_category(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post("/yummy/api/v1.0/recipe_categories/", **self.kwargs)

        # change category details
        self.sample_categories[0]["cat_name"] = "New Recipe Edited"
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        edit_response = self.test_client().put("/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn("Successfully edited recipe category", edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 200)

    def test_cant_edit_category_that_belongs_to_another_user(self):
        """ Register and login two users """
        login_responses = [self.register_and_login_user(),
                           self.register_and_login_user(self.user_details2, self.login_details2)]
        login_tokens = [self.get_token_from_response(login_response) for login_response in login_responses]

        # create category using the first user
        self.kwargs["data"] = json.dumps({"cat_name": "This is new"})
        self.kwargs["headers"] = {"x-access-token": login_tokens[0]}
        response = self.test_client().post("/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        # try editing category details using the second user
        self.sample_categories[0]["cat_name"] = "New Recipe Edited"
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_tokens[1]}
        edit_response = self.test_client().put("/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn("The recipe category you are trying to modify does not belong to you",
                      edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 403)

    def test_cant_edit_category_when_logged_out(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post("/yummy/api/v1.0/recipe_categories/", **self.kwargs)

        # change category name to the same name
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs.pop("headers")
        edit_response = self.test_client().put("/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn("The access token is required", edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 401)

    def test_category_isnt_edited_if_current_and_new_category_names_are_similar(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post("/yummy/api/v1.0/recipe_categories/", **self.kwargs)

        # change category name to the same name
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        edit_response = self.test_client().put("/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn("The new recipe category name you are trying to use already exists", edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 400)

    def test_cant_edit_category_that_doesnot_exist(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post("/yummy/api/v1.0/recipe_categories/", **self.kwargs)

        # change category details
        self.sample_categories[0]["cat_name"] = "New Recipe Edited"
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        edit_response = self.test_client().put("/yummy/api/v1.0/recipe_categories/2", **self.kwargs)
        self.assertIn("The recipe category you are trying to modify does not exist", edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 404)

    def test_user_can_delete_recipe_category(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post("/yummy/api/v1.0/recipe_categories/", **self.kwargs)

        # delete the category
        self.kwargs.pop("data")
        delete_response = self.test_client().delete("/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertEqual(delete_response.status_code, 200)
        self.assertIn("Recipe Category successfully deleted", delete_response.data.decode())

    def test_cant_delete_a_category_that_belongs_to_another_user(self):
        """Register and login two users """
        login_responses = [self.register_and_login_user(),
                           self.register_and_login_user(self.user_details2, self.login_details2)]
        login_tokens = [self.get_token_from_response(login_response) for login_response in login_responses]

        # create category using the first user
        self.kwargs["data"] = json.dumps({"cat_name": "This is new"})
        self.kwargs["headers"] = {"x-access-token": login_tokens[0]}
        response = self.test_client().post("/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        # try deleting category  using the second user
        self.kwargs.pop("data")
        self.kwargs["headers"] = {"x-access-token": login_tokens[1]}
        delete_response = self.test_client().delete("/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn("The recipe category you are trying to modify does not belong to you",
                      delete_response.data.decode())
        self.assertEqual(delete_response.status_code, 403)

    def test_user_cant_delete_a_category_that_doesnot_exist(self):
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # delete a category that does not exist
        self.kwargs["headers"] = {"x-access-token": login_token}
        delete_response = self.test_client().delete("/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertEqual(delete_response.status_code, 404)
        self.assertIn("The recipe category you are trying to modify does not exist", delete_response.data.decode())

    def test_can_get_all_user_categories(self):
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create some recipe categories
        responses = [self.create_recipe_category(recipe_cat, login_token) for recipe_cat in self.sample_categories]

        # fetch all the categories
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().get("/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Recipe Categories exists", response.data.decode())

    def test_can_get_all_recipes_in_a_category(self):
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create a recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)

        # add recipes to the recipe category
        add_recipe_responses = [self.create_recipe(recipe, login_token) for recipe in self.sample_recipes]
        # fetch the recipes is the category
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().get("/yummy/api/v1.0/recipe_categories/1/recipes/", **self.kwargs)
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
        self.assertIn(self.sample_categories[0]["cat_name"], response.data.decode())
        self.assertEqual(response.status_code, 200)

    def test_can_add_recipe(self):
        pass

    def test_cant_add_recipe_in_a_category_that_doenot_exist(self):
        pass

    def test_cant_add_recipe_to_a_category_that_belongs_to_another_user(self):
        pass

    def test_cant_add_recipe_in_a_category_where_another_recipe_with_same_name_exists(self):
        pass

    def test_cant_add_recipe_if_invalid_data_is_supplied(self):
        pass

    def test_cant_edit_recipe(self):
        pass

    def test_cant_edit_recipe_category_to_a_category_that_doesnot_exist(self):
        pass

    def test_cant_edit_recipe_category_to_a_category_that_doesnot_belong_to_you(self):
        pass

    def test_cane_edit_recipe_that_doesnt_belong_to_you(self):
        pass

    def test_cant_edit_recipe_that_doesnot_exist(self):
        pass

    def test_can_publish_recipe(self):
        pass

    def cant_publish_another_users_recipe(self):
        pass

    def test_can_delete_recipe(self):
        pass

    def test_cant_delete_another_users_recipe(self):
        pass

    def test_can_get_all_user_recipes(self):
        pass

    def test_can_get_single_recipe(self):
        pass

    def create_recipe(self, recipe_details, login_token):
        self.kwargs["data"] = json.dumps(recipe_details)
        self.kwargs["headers"] = {"x-access-token": login_token}
        return self.test_client().post("/yummy/api/v1.0/recipes/", **self.kwargs)

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
        headers = {"Authorization": f"Basic {b64encode(bytes(credentials,'utf-8')).decode('ascii')}"}
        return self.test_client().post("/yummy/api/v1.0/auth/login/", headers=headers)

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
        self.user = User("dennisjjagwe@gmail.com", "jjagwe", "dennis", "mypassword")

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


if __name__ == "__main__":
    unittest.main()
