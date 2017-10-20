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
            "category": "Category"
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

            return self.__errors

        except KeyError as er:
            raise ValidationError("Validation failure: Check that you sent all the required data and try again")
