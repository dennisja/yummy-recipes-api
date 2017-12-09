"""
This module has methods to test the validator class
"""
import unittest

from api.validator import Validate, ValidationError


class ValidatorTestCases(unittest.TestCase):
    def setUp(self):
        self.validator = Validate()

    def test_empty_required_submitted_value(self):
        """ tests if validation fails if a required field isnt submitted """
        form_data = {"lastname": ""}
        rules = {"lastname": {"required": True}}
        self.assertTrue(self.validator.validate_data(form_data, rules))

    def test_no_number_in_submitted_value(self):
        """ tests if validation fails if a number is submitted in field its not required """
        form_data = {"lastname": "d56"}
        rules = {"lastname": {"no_number": True}}
        self.assertTrue(self.validator.validate_data(form_data, rules))

    def test_min_length_of_submitted_value(self):
        """ tests if validation fails if a field has a length less than the required length """
        form_data = {"lastname": "den"}
        rules = {"lastname": {"min": 6}}
        self.assertTrue(self.validator.validate_data(form_data, rules))

    def test_max_length_of_submitted_value(self):
        """ tests if validation fails if a field has a length greater than the required length """
        form_data = {"lastname": "denhhhhh"}
        rules = {"lastname": {"max": 6}}
        self.assertTrue(self.validator.validate_data(form_data, rules))

    def test_invalid_key_from_in_user_data(self):
        """ tests if a validation error is raised if missing keys are used """
        form_data = {"absent_key": ""}
        rules = {"absent_key": {"required": True}}
        self.assertRaises(
            ValidationError,
            self.validator.validate_data,
            source=form_data,
            items=rules)
