""" This module has tests of the user model
"""
import unittest

from api.models import User


class UserModelTestCase(unittest.TestCase):
    """ The class has methods to test the use model """

    def setUp(self):
        self.user = User("dennisjjagwe@gmail.com", "jjagwe", "dennis",
                         "mypassword")

    def test_no_id(self):
        """ tests whether user will have no id before being saved to the database """
        self.assertTrue(self.user.id is None)

    def test_verify_password(self):
        """ ensures that the verify password method works fine """
        self.assertTrue(self.user.verify_password("mypassword"))

    def test_set_password(self):
        """ ensures that the set password method of the user model works fine"""
        self.user.set_password("new_password")
        self.assertTrue(self.user.verify_password("new_password"))

    def test_set_password_fail(self):
        """ ensures that the set password method of the user model works fine"""
        self.user.set_password("new_password")
        self.assertFalse(self.user.verify_password("mypassword"))

    def test_different_passwords(self):
        """ tests if two users with the same password string will have different password hashes """
        user1 = User("dennisj@gmail.com", "jjagwe", "denni", "password")
        user2 = User("dennisj@gmail.com", "king", "dennis", "password")
        self.assertNotEqual(user1.password, user2.password)
