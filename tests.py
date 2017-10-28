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
