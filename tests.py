from api import app
from api.models import User, Recipe, RecipeCategory
import unittest

class ApiBasicsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app

    def test_app_is_not_null(self):
        self.assertTrue(self.app is not None)



class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.user = User("dennisjjagwe@gmail.com","jjagwe","dennis","mypassword")


    def test_verify_password(self):
        self.assertTrue(self.user.verify_password("mypassword"))
        self.assertFalse(self.user.verify_password("otherpassword"))

    def test_set_password(self):
        self.user.set_password("new_password")
        self.assertTrue(self.user.verify_password("new_password"))
        self.assertFalse(self.user.verify_password("mypassword"))

if __name__ == "__main__":
    unittest.main()