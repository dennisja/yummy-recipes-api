import unittest

from api.validator import Validate, ValidationError


class ValidatorTestCases(unittest.TestCase):
    def setUp(self):
        self.validator = Validate()

    def test_empty_required_submitted_value(self):
        form_data = {"lastname": ""}
        rules = {"lastname": {
            "required": True
        }}
        self.assertTrue(self.validator.validate_data(form_data, rules))

    def test_no_number_in_submitted_value(self):
        form_data = {"lastname": "d56"}
        rules = {"lastname": {
            "no_number": True
        }}
        self.assertTrue(self.validator.validate_data(form_data, rules))

    def test_min_length_of_submitted_value(self):
        form_data = {"lastname": "den"}
        rules = {"lastname": {
            "min": 6
        }}
        self.assertTrue(self.validator.validate_data(form_data, rules))

    def test_max_length_of_submitted_value(self):
        form_data = {"lastname": "denhhhhh"}
        rules = {"lastname": {
            "max": 6
        }}
        self.assertTrue(self.validator.validate_data(form_data, rules))

    def test_invalid_key_from_in_user_data(self):
        form_data = {
            "absent_key": ""
        }
        rules = {"absent_key": {
            "required": True
        }}
        self.assertRaises(KeyError, self.validator.validate_data,
                          source=form_data, items=rules)
