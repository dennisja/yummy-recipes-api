from api import app, db
from api.models import User, Recipe, RecipeCategory
import unittest


class ApiBasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.config[
            "SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:mypassword@127.0.0.1:5432/test_yummy_recipes"
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_is_not_null(self):
        self.assertTrue(self.app is not None)

    def test_app_is_using_test_database(self):
        self.assertEqual(self.app.config["SQLALCHEMY_DATABASE_URI"], "postgresql://postgres:mypassword@127.0.0.1:5432/test_yummy_recipes")


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
