from api import app, db
from api.models import User, Recipe, RecipeCategory
import unittest
import json


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

        self.kwargs = {"content_type":'application/json'}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

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
        self.assertIn("Validation failure: Check that you sent all the required data and try again", str(response.data.decode("utf-8")))

    def test_user_registration_fails_if_invalid_data_is_sent(self):
        invalid_data = self.user_details1
        invalid_data["firstname"] = "g56"
        invalid_data["password"] = "pass"
        self.kwargs.setdefault("data", json.dumps(invalid_data))
        response = self.test_client().post("/yummy/api/v1.0/auth/register/", **self.kwargs)
        self.assertTrue(response.status_code, 422)
        self.assertIn("First Name must contain no digits",response.data.decode())
        self.assertIn("Password must be a minimum of 8 characters", response.data.decode())
        self.assertIn("Password must match Confirm Password", response.data.decode())

    def test_user_registers_successfully_if_correct_data_is_sent(self):
        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        response = self.test_client().post("/yummy/api/v1.0/auth/register/", **self.kwargs)
        response_string = response.data.decode()
        self.assertEqual(response.status_code, 201)
        self.assertIn("You have been successfully registered and you can now login", response_string)
        self.assertIn(self.user_details1["firstname"], response_string)
        self.assertIn(self.user_details1["lastname"], response_string)

    def test_cant_register_user_who_alreafy_exists(self):
        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        # register a user
        self.test_client().post("/yummy/api/v1.0/auth/register/", **self.kwargs)
        # try registering the user again
        response1 = self.test_client().post("/yummy/api/v1.0/auth/register/", **self.kwargs)
        response_string = response1.data.decode()
        self.assertEqual(response1.status_code, 422)
        self.assertIn(f"Email address \'{self.user_details1['email']}\' already in use", response_string)

    def test_user_cant_login_if_some_data_is_missing(self):
        pass

    def test_user_cant_login_if_sent_data_has_validation_errors(self):
        pass

    def test_user_cant_login_if_he_has_not_yet_registered(self):
        pass

    def test_user_cant_login_if_he_supplies_a_wrong_password(self):
        pass

    def test_user_can_login_with_correct_credentials(self):
        pass

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
