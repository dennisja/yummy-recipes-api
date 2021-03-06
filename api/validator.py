"""This is the validator module
It contains the Validate class to perform user data validation
ValidateUser class has rules to validate user data when registering, editing or loggin in a users
ValidateRecipe class has rules to validate data when adding and creating a recipe
ValidateRecipeCategory has rules to validate data when adding and creating a recipe category
"""
import re


class ValidationError(KeyError):
    """ Raised if a missing key of the __display dictionary is accessed or
    A request is sent with a missing key
    """
    pass


class Validate:
    """ Used to validate data """

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
            "cat_name": "Category Name",
            "steps": "Steps",
            "ingredients": "Ingredients"
        }

    def validate_data(self, source, items):
        """ Performs validation of data
        """
        try:
            for each_item, each_item_rules in items.items():
                for each_rule, each_rule_value in each_item_rules.items():
                    value = str(source[each_item]).strip()
                    item = each_item

                    if each_rule == "required" and not len(value):
                        self.__errors.append("{} is required".format(
                            self.__display[item]))
                    else:
                        if each_rule == "min" and len(value) < each_rule_value:
                            self.__errors.append(
                                f"{self.__display[item]} must be a minimum of {each_rule_value} characters"
                            )

                        if each_rule == "numeric" and not str(
                                value).isdecimal():
                            self.__errors.append(
                                f"{self.__display[item]} must be a number")

                        if each_rule == "max" and len(value) > each_rule_value:
                            self.__errors.append(
                                f"{self.__display[item]} must be a maximum of {each_rule_value} characters"
                            )

                        if each_rule == "no_number" and bool(
                                re.compile("[0-9]").search(value)):
                            self.__errors.append(
                                f"{self.__display[item]} must contain no digits"
                            )

                        if each_rule == "matches" and each_rule_value in source and value != source[each_rule_value]:
                            self.__errors.append("{} must match {}".format(
                                self.__display[each_rule_value],
                                self.__display[item]))

                        if each_rule == "email" and not re.search(
                                r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                                value):
                            self.__errors.append("{} is invalid".format(
                                self.__display[item]))

                        if each_rule == "not_equal_to" and each_rule_value in source and value == source[each_rule_value]:
                            self.__errors.append(
                                f"{self.__display[each_rule_value]} must not be equal to {self.__display[item]}")

                        if each_rule == "no_characters" and re.search(
                                r"[@#$%^&\*()\{\}\[\]\+=!~\/\\|\.]+", value):
                            self.__errors.append(
                                f"{self.__display[item]} must not contain non word characters"
                            )
            validation_errors = self.__errors
            # resetting the errors array
            self.__errors = list()
            return validation_errors

        except KeyError:
            raise ValidationError(
                "Validation failure: Check that you sent all the required data and try again"
            )


class ValidateUser():
    """Has methods to validate user data when logging in, registering,
    changing password and editing user details"""
    validator = Validate()
    __password_rules = {"required": True, "min": 8, "max": 20}
    __email_rules = {"required": True, "email": True, "min": 8, "max": 100}

    @staticmethod
    def validate_user_on_reg(user_registration_details, action="create"):
        """ Validates user data when registering or editing user details"""
        rules = {
            "firstname": {
                "required": True,
                "max": 20,
                "no_number": True,
                "no_characters": True
            },
            "lastname": {
                "required": True,
                "max": 40,
                "no_number": True,
                "no_characters": True
            },
            "email": ValidateUser.__email_rules,
            "password": ValidateUser.__password_rules,
            "c_password": {
                "matches": "password"
            }
        }

        # remove password and c-password when editing user data
        if action == "edit":
            rules.pop("password")
            rules.pop("c_password")

        validation_errors = ValidateUser.validator.validate_data(
            user_registration_details, rules)
        return validation_errors

    @staticmethod
    def validate_user_login(login_details):
        """ Validates user login details """
        login_errors = ValidateUser.validator.validate_data(
            login_details, {
                "username": ValidateUser.__email_rules,
                "password": ValidateUser.__password_rules
            })
        return login_errors

    @staticmethod
    def validate_password_data(user_data):
        """ Validates user data submitted when changing a password """
        new_password_rules = dict(ValidateUser.__password_rules)
        new_password_rules["not_equal_to"] = "current_password"

        password_errors = ValidateUser.validator.validate_data(
            user_data, {
                "current_password": ValidateUser.__password_rules,
                "new_password": new_password_rules,
                "new_password_again": {
                    "matches": "new_password"
                }
            })
        return password_errors


class ValidateRecipeCategory:
    """ Has a method to validate data when adding and editing a recipe category """
    __validator = Validate()

    @staticmethod
    def validate_recipe(recipe_data):
        """ Validates data when adding and editing a recipe category """
        recipe_errors = ValidateRecipeCategory.__validator.validate_data(
            recipe_data, {
                "cat_name": {
                    "required": True,
                    "no_number": True,
                    "min": 3,
                    "max": 200
                }
            })
        return recipe_errors


class ValidateRecipe:
    """ Has a method to validate data passed when adding a Recipe"""
    __validator = Validate()

    @staticmethod
    def validate_recipe(recipe_data):
        """ Validates data when adding and editing a recipe """
        recipe_errors = ValidateRecipe.__validator.validate_data(
            recipe_data, {
                "name": {
                    "required": True,
                    "min": 3,
                    "max": 200
                },
                "steps": {
                    "required": True,
                    "min": 10,
                    "max": 1000
                },
                "ingredients": {
                    "required": True,
                    "min": 10,
                    "max": 500
                },
                "category": {
                    "required": True,
                    "numeric": True
                }
            })
        return recipe_errors
