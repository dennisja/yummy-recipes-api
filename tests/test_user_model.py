""" This module has tests of the user model
"""
import unittest

from api.models import User


class UserModelTestCase(unittest.TestCase):
    """ The class has methods to test the use model """

    def setUp(self):
        self.user = User("dennisjjagwe@gmail.com", "jjagwe", "dennis",
                         "mypassword")

    def test_user_has_no_id_before_addition_to_database(self):
        """ tests whether user will have no id before being saved to the database """
        self.assertFalse(self.user.id is not None)
        self.assertTrue(self.user.id is None)

    def test_verify_password(self):
        """ ensures that the verify password method works fine """
        self.assertTrue(self.user.verify_password("mypassword"))
        self.assertFalse(self.user.verify_password("otherpassword"))

    def test_set_password(self):
        """ ensures that the set password method of the user model works fine"""
        self.user.set_password("new_password")
        self.assertTrue(self.user.verify_password("new_password"))
        self.assertFalse(self.user.verify_password("mypassword"))

    def test_stored_passwords_are_random_if_password_strings_are_similar(self):
        """ tests if two users with the same password string will have different password hashes """
        user1 = User("dennisj@gmail.com", "jjagwe", "denni", "password")
        user2 = User("dennisj@gmail.com", "king", "dennis", "password")
        self.assertTrue(user1.password != user2.password)
        self.assertFalse(user2.password == user1.password)
