import re


class ValidationError(KeyError):
    pass


class Validate:
    def __init__(self):
        self.__passes = False
        self.__errors = list()
        self.__display = {
            "firstname": "First Name",
            "lastname": "Last Name",
            "email": "Email",
            "password": "Password",
            "c_password": "Confirm Password",
            "name": "Name",
            "description": "Description",
            "category": "Category",
            "username": "Email",
            "current_password": "Current Password",
            "new_password": "New Password",
            "new_password_again": "Retyped New Password",
            "cat_name": "Category Name"
        }

    def validate_data(self, source, items):
        try:
            for each_item, each_item_rules in items.items():
                for each_rule, each_rule_value in each_item_rules.items():
                    value = source[each_item].strip()
                    item = each_item

                    if each_rule == "required" and not len(value):
                        self.__errors.append(
                            "{} is required".format(self.__display[item]))
                    else:
                        if each_rule == "min" and len(value) < each_rule_value:
                            self.__errors.append(
                                "{} must be a minimum of {} characters".format(self.__display[item], each_rule_value))

                        if each_rule == "max" and len(value) > each_rule_value:
                            self.__errors.append(
                                "{} must be a maximum of {} characters".format(self.__display[item], each_rule_value))

                        if each_rule == "no_number" and bool(re.compile("[0-9]").search(value)):
                            self.__errors.append(
                                "{} must contain no digits".format(self.__display[item]))

                        if each_rule == "matches" and each_rule_value in source and value != source[each_rule_value]:
                            self.__errors.append("{} must match {}".format(
                                self.__display[each_rule_value], self.__display[item]))

                        if each_rule == "email" and not re.compile("[@]").search(value):
                            self.__errors.append(
                                "{} is invalid".format(self.__display[item]))

                        if each_rule == "not_equal_to" and each_rule_value in source and value == source[
                            each_rule_value]:
                            self.__errors.append(
                                f"{self.__display[each_rule_value]} must not be equal to {self.__display[item]}")

            return self.__errors

        except KeyError as er:
            raise ValidationError("Validation failure: Check that you sent all the required data and try again")


class ValidateUser():
    validator = Validate()

    @staticmethod
    def validate_user_on_reg(user_registration_details, action="create"):
        """ Action to perform on a user"""
        rules = {
            "firstname": {
                "required": True,
                "max": 20,
                "no_number": True
            },
            "lastname": {
                "required": True,
                "max": 20,
                "no_number": True
            },
            "email": {
                "required": True,
                "email": True,
                "min": 8,
                "max": 100
            },
            "password": {
                "required": True,
                "min": 8,
                "max": 20
            },
            "c_password": {
                "matches": "password"
            }
        }

        # remove password and c-password when editing user data
        if action == "edit":
            rules.pop("password")
            rules.pop("c_password")

        validation_errors = ValidateUser.validator.validate_data(user_registration_details, rules)
        return validation_errors

    @staticmethod
    def validate_user_login(login_details):
        """ Validates user login details """
        login_errors = ValidateUser.validator.validate_data(login_details, {
            "username": {
                "required": True,
                "email": True,
                "min": 8,
                "max": 100
            },
            "password": {
                "required": True,
                "min": 8,
                "max": 20
            }
        })
        return login_errors

    @staticmethod
    def validate_password_data(user_data):
        """ Validates user data submitted when changing a password """
        password_errors = ValidateUser.validator.validate_data(user_data, {
            "current_password": {
                "required": True,
                "min": 8,
                "max": 20
            },
            "new_password": {
                "required": True,
                "min": 8,
                "max": 20,
                "not_equal_to": "current_password"
            },
            "new_password_again": {
                "matches": "new_password"
            }
        })
        return password_errors


class ValidateRecipeCategory:
    __validator = Validate()

    @staticmethod
    def validate_recipe(recipe_data):
        recipe_errors = ValidateRecipeCategory.__validator.validate_data(recipe_data, {
            "cat_name": {
                "required": True,
                "no_number": True,
                "min": 3,
                "max": 200
            }
        })
        return recipe_errors
