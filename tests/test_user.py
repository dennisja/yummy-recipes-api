""" This module tests all user actions in the api like registration,
 login, editing user details, changing password e.t.c"""
import json
from base64 import b64encode

from tests import ApiBasicsTestCase


class UserTestCases(ApiBasicsTestCase):
    """ Has methods to test for user actions """

    def test_no_data(self):
        """ tests if user registration fails if no data is sent """
        response = self.test_client().post("/yummy/api/v1.0/auth/register/")
        response_data = json.loads(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 400)
        self.assertTrue("Request not Understood" in response_data["errors"])

    def test_incomplete_data(self):
        """ tests if user registration fails if incomplete data is sent """
        user_data = self.user_details1
        user_data.pop("password")
        self.kwargs.setdefault("data", json.dumps(user_data))
        response = self.test_client().post("/yummy/api/v1.0/auth/register/",
                                           **self.kwargs)
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Validation failure: Check that you sent all the required data and try again",
            str(response.data.decode("utf-8")))

    def test_invalid_data(self):
        """ test whther user registration fails if invalid data is sent"""
        invalid_data = dict(self.user_details1)
        invalid_data["firstname"] = "g56"
        invalid_data["password"] = "pass"
        self.kwargs.setdefault("data", json.dumps(invalid_data))
        response = self.test_client().post("/yummy/api/v1.0/auth/register/",
                                           **self.kwargs)
        self.assertTrue(response.status_code, 422)
        self.assertIn("First Name must contain no digits",
                      response.data.decode())
        self.assertIn("Password must be a minimum of 8 characters",
                      response.data.decode())
        self.assertIn("Password must match Confirm Password",
                      response.data.decode())

    def test_register_user(self):
        """ test can register a user with invalid data """
        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        # register a user
        response1 = self.test_client().post("/yummy/api/v1.0/auth/register/",
                                            **self.kwargs)
        self.assertEqual(response1.status_code, 201)
        response_string = response1.data.decode()
        self.assertIn(
            "You have been successfully registered and you can now login",
            response_string)
        self.assertIn(self.user_details1["firstname"], response_string)
        self.assertIn(self.user_details1["lastname"], response_string)

    def test_user_exists(self):
        """ test whether a user cant register with an alrerady used email"""
        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        # register a user
        self.test_client().post("/yummy/api/v1.0/auth/register/",
                                **self.kwargs)
        # try registering the user again
        response1 = self.test_client().post("/yummy/api/v1.0/auth/register/",
                                            **self.kwargs)
        response_string = response1.data.decode()
        self.assertEqual(response1.status_code, 422)
        self.assertIn(
            f"Email address \'{self.user_details1['email']}\' already in use",
            response_string)

    def test_missing_login(self):
        """ test whether a user cant login if some data is missing """
        # try logging in with no login data sent
        response = self.test_client().post("/yummy/api/v1.0/auth/login/")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing login credentials", response.data.decode())
        # try logging in with only username
        headers = {
            "Authorization":
            f"Basic {b64encode(bytes('dennisjjagwe@gmail.com','utf-8')).decode('ascii')}"
        }
        response1 = self.test_client().post(
            "/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertEqual(response1.status_code, 400)
        self.assertIn("Missing login credentials", response1.data.decode())

    def test_invalid_login(self):
        """ tests ehether login fails if invalid data is sent """
        headers = {
            "Authorization":
            f"Basic {b64encode(bytes('dennisjjagwe:myp','utf-8')).decode('ascii')}"
        }
        response1 = self.test_client().post(
            "/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertEqual(response1.status_code, 401)
        self.assertIn("Email is invalid", response1.data.decode())
        self.assertIn("Password must be a minimum of 8 characters",
                      response1.data.decode())
        self.assertIn("Invalid login credentials", str(response1.headers))

    def test_not_registered(self):
        """ tests whether login fails if user is not yet registered"""
        credentials = f"{self.user_details1['email']}:{self.user_details1['password']}"
        headers = {
            "Authorization":
            f"Basic {b64encode(bytes(credentials,'utf-8')).decode('ascii')}"
        }
        response = self.test_client().post(
            "/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertTrue(response.status_code, 404)
        self.assertIn(
            f"Email '{self.user_details1['email']}' is not yet registered",
            response.data.decode())

    def test_wrong_password(self):
        """ test user cant login with long password """
        credentials = f"{self.user_details1['email']}:wrongpassword"
        headers = {
            "Authorization":
            f"Basic {b64encode(bytes(credentials,'utf-8')).decode('ascii')}"
        }

        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        # register a user
        self.test_client().post("/yummy/api/v1.0/auth/register/",
                                **self.kwargs)

        # login user with wrong password
        login_response = self.test_client().post(
            "/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertEqual(login_response.status_code, 401)
        self.assertIn("Invalid email and password combination",
                      str(login_response.headers))

    def test_correct_credentials(self):
        """ test user can login with correct credentials """
        credentials = f"{self.user_details1['email']}:{self.user_details1['password']}"
        headers = {
            "Authorization":
            f"Basic {b64encode(bytes(credentials,'utf-8')).decode('ascii')}"
        }

        self.kwargs.setdefault("data", json.dumps(self.user_details1))
        # register a user
        self.test_client().post("/yummy/api/v1.0/auth/register/",
                                **self.kwargs)

        # login user with wrong password
        login_response = self.test_client().post(
            "/yummy/api/v1.0/auth/login/", headers=headers)
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("token", login_response.data.decode())
        self.assertTrue(
            json.loads(login_response.data.decode())["token"] is not None)

    def test_expired_token(self):
        """ tests whether a user cant edit details with an expired token """
        self.register_user(self.user_details1)
        self.kwargs["data"] = json.dumps({
            "firstname": "Jonah",
            "lastname": "Pat",
            "email": self.user_details2["email"]
        })
        self.kwargs["headers"] = {"x-access-token": self.expired_token}
        response = self.test_client().put("/yummy/api/v1.0/users/",
                                          **self.kwargs)
        self.assertEqual(response.status_code, 401)
        # self.assertIn("The token has expired", response.data.decode())

    def test_no_token(self):
        """ test cant edit user detals if the auth token is absent """
        self.register_user(self.user_details1)
        self.kwargs["data"] = json.dumps({
            "firstname": "Jonah",
            "lastname": "Pat",
            "email": self.user_details2["email"]
        })
        response = self.test_client().put("/yummy/api/v1.0/users/",
                                          **self.kwargs)
        self.assertEqual(response.status_code, 401)
        self.assertIn("The access token is required", response.data.decode())

    def test_edit_profile(self):
        """ test whether user cant edit another user's details """
        # register two users
        self.register_user(self.user_details1)
        login_response = self.login_user(self.login_details1)
        login_token = self.get_token_from_response(login_response)
        self.kwargs["data"] = json.dumps({
            "firstname": "Jonah",
            "lastname": "Pat",
            "email": self.user_details2["email"]
        })
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().put("/yummy/api/v1.0/users/",
                                          **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertIn("All changes where applied successfully",
                      response.data.decode())

    def test_edit_email(self):
        """ test whether editing email to another user's email fails"""
        # register two users, login them and get their login tokens
        reg_responses = [
            self.register_user(self.user_details1),
            self.register_user(self.user_details2)
        ]
        login_responses = [
            self.login_user(self.login_details1),
            self.login_user(self.login_details2)
        ]
        login_tokens = [
            self.get_token_from_response(response)
            for response in login_responses
        ]

        # try changing one of the user email to that of the other user
        self.kwargs["data"] = json.dumps({
            "firstname": "Jonah",
            "lastname": "Pat",
            "email": self.user_details2["email"]
        })
        self.kwargs["headers"] = {"x-access-token": login_tokens[0]}

        response = self.test_client().put("/yummy/api/v1.0/users/",
                                          **self.kwargs)
        data = response.data.decode()
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            f"The email \'{self.user_details2['email']}\' is already in use",
            data)

    def test_similar_password(self):
        """ tests if changing password to a similar password fails"""
        response = self.get_response_on_change_password(
            current="password",
            newpassword="password",
            newpassword_again="password")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Current Password must not be equal to New Password",
                      str(response.data))

    def test_wrong_pwd(self):
        """ tests changing """
        response = self.get_response_on_change_password()
        self.assertEqual(response.status_code, 403)
        self.assertIn("The current password supplied is wrong",
                      response.data.decode())

    def test_change_password(self):
        """ tests whether user can change his/her password with right credentials """
        response = self.get_response_on_change_password(current="password")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Password Changed Successfully", response.data.decode())

    def test_retrieving_all_users(self):
        """ tests retrieving all user data """
        # register users
        self.register_user(self.user_details1)
        self.register_user(self.user_details2)
        login_token = self.get_token_from_response(
            self.login_user(self.login_details1))
        response = self.test_client().get(
            "/yummy/api/v1.0/users/", headers={
                "x-access-token": login_token
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn("users", response.data.decode())
        self.assertIn(self.user_details1["firstname"], response.data.decode())
        self.assertIn(self.user_details2["firstname"], response.data.decode())

    def test_no_user_exist(self):
        """ test if no user found is returned if no registered users """
        login_token = self.register_login_delete_user()
        response = self.test_client().get(
            "/yummy/api/v1.0/users/", headers={
                "x-access-token": login_token
            })
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.data.decode())

    def test_user_data(self):
        """ tests the end point that retrieves single user data """
        # register a user
        reg_response = self.register_user(self.user_details1)
        login_response = self.login_user(self.login_details1)
        user_url = json.loads(reg_response.data.decode())["data"]["url"]

        # access registered user
        user_response = self.test_client().get(
            user_url,
            headers={
                "x-access-token": self.get_token_from_response(login_response)
            })
        self.assertEqual(user_response.status_code, 200)
        self.assertIn(self.user_details1["email"], user_response.data.decode())

    def test_invalid_id(self):
        """ tests whether getting a user with an ivalid id fails """
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # try using an invalid public id
        response = self.test_client().get(
            "/yummy/api/v1.0/users/1/",
            headers={
                "x-access-token": login_token
            })
        self.assertEqual(response.status_code, 400)
        self.assertIn("Request not Understood", response.data.decode())
