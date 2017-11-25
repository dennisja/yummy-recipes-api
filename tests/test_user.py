import json

from tests import ApiBasicsTestCase
from base64 import b64encode


class UserTestCases(ApiBasicsTestCase):

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
        self.assertIn(
            "Current Password must not be equal to New Password", response.data.decode())

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
