from api import app, models, db
from api.helpers import Secure, TokenError, TokenExpiredError
from api.validator import ValidationError, ValidateUser
from api.decorators import auth_token_required, json_data_required
from flask import make_response, jsonify, abort, request, url_for
from itsdangerous import BadSignature


@app.route("/yummy/api/v1.0/auth/register/", methods=["POST"])
def register_user():
    """ Registers a yummy recipes user """
    if not request.json:
        abort(400)

    # validate the user
    validation_errors = ValidateUser.validate_user_on_reg(request.json)

    # check if errors occurred
    if validation_errors:
        return jsonify({"errors": validation_errors}), 422

    # check if user already exists
    existing_user = models.User.query.filter_by(email=request.json["email"]).first()
    if existing_user:
        return jsonify({"errors": ["Email address '{}' already in use".format(request.json["email"])]}), 422

    # register the user
    user = models.User(request.json["email"], request.json["firstname"],
                       request.json["lastname"], request.json["password"])
    user.save_user()

    return jsonify(
        {"messages": ["You have been successfully registered and you can now login"], "data": user.user_details}), 201


@app.route("/yummy/api/v1.0/auth/login/", methods=["POST"])
def login_user():
    auth_details = request.authorization
    # check whether authorization details are supplied
    if not auth_details or not "username" in auth_details or not "password" in auth_details:
        return jsonify({"errors": ["Missing login credentials"]}), 400
    # validate sent details
    validation_errors = ValidateUser.validate_user_login(auth_details)
    if validation_errors:
        return jsonify({"errors": validation_errors}), 401, {
            "WWW-Authenticate": "Basic realm='Invalid login credentials'"}

    # check if a user exists
    user = models.User.query.filter_by(email=auth_details["username"]).first()
    if not user:
        raise models.UserNotFoundError(f"Email '{auth_details['username']}' is not yet registered")

    # if user password is correct
    if user.verify_password(auth_details["password"]):
        access_token = Secure.generate_auth_token(user.id)
        return jsonify({"message": "Successfully logged in", "token": access_token}), 200
        # generate and return the token

    return jsonify({"errors": ["Invalid email and password combination"]}), 401, {
        "WWW-Authenticate": "Basic realm='Invalid email and password combination'"}


# recipe category end points
@app.route("/yummy/api/v1.0/recipe_categories/", methods=["POST"])
@auth_token_required
def add_recipe_category(user):
    """ Adds a recipe category """
    return "s"


@app.route("/yummy/api/v1.0/recipe_categories/<int:category_id>/", methods=["PUT"])
@auth_token_required
def edit_recipe_category(user, category_id):
    """ Edits a recipe category """
    return ""


@app.route("/yummy/api/v1.0/recipe_categories/<int:category_id>/", methods=["DELETE"])
@auth_token_required
def delete_recipe_category(user, category_id):
    """ Deletes a recipe category """
    return ""


@app.route("/yummy/api/v1.0/recipe_categories/", methods=["GET"])
@auth_token_required
def get_all_user_recipe_categories(user):
    """ Gets all user recipe categories """
    return ""


@app.route("/yummy/api/v1.0/recipe_categories/<int:category_id>/recipes/", methods=["GET"])
@auth_token_required
def get_all_recipes_in_a_category(user, category_id):
    """ Gets user recipes in a particular category """
    return ""


# recipe end points
@app.route("/yummy/api/v1.0/recipes/", methods=["POST"])
@auth_token_required
def add_recipe(user):
    """ Adds a recipe """
    return jsonify({"user": user.user_details})


@app.route("/yummy/api/v1.0/recipes/<int:recipe_id>/", methods=["PUT"])
@auth_token_required
def edit_a_recipe(user, recipe_id):
    """ Edits a recipe """
    return ""


@app.route("/yummy/api/v1.0/recipes/<int:recipe_id>/", methods=["PATCH"])
@auth_token_required
def publish_recipe(user, recipe_id):
    """ Publishes or un publishes a recipe """
    return ""


@app.route("/yummy/api/v1.0/recipes/<int:recipe_id>/", methods=["DELETE"])
@auth_token_required
def delete_recipe(user, recipe_id):
    """ Deletes a single recipe """
    return ""


@app.route("/yummy/api/v1.0/recipes/", methods=["GET"])
@auth_token_required
def get_all_user_recipes(user):
    """ Gets user recipes """
    return ""


@app.route("/yummy/api/v1.0/recipes/<int:recipe_id>/", methods=["GET"])
@auth_token_required
def get_recipe(user, recipe_id):
    """ Gets a single recipe """
    return ""


# user end points
@app.route("/yummy/api/v1.0/users/", methods=["PUT"])
@json_data_required
@auth_token_required
def edit_user_details(user):
    """ Updates user details """
    # validate user data
    edit_errors = ValidateUser.validate_user_on_reg(request.json, action="edit")

    if edit_errors:
        return jsonify({"errors": edit_errors}), 400

    user.email = request.json.get("email")
    user.firstname = request.json.get("firstname")
    user.lastname = request.json.get("lastname")

    db.session.commit()
    return jsonify({"message":"All chages where applied succesfully"}), 200, {"Location":user.user_details["url"]}


@app.route("/yummy/api/v1.0/users/", methods=["PATCH"])
@json_data_required
@auth_token_required
def change_user_password(user):
    """ Changes a user password """
    # validate sent data
    password_errors = ValidateUser.validate_password_data(request.json)

    if password_errors:
        return jsonify({"errors":password_errors}), 400

    if not user.verify_password(request.json.get("current_password")):
        return jsonify({"errors":["The current password supplied is wrong"]}), 403

    user.set_password(request.json.get("new_password"))
    db.session.commit()

    # change the password if no error has occurred
    return jsonify({"message":"Password Changed Successfully"}), 200


@app.route("/yummy/api/v1.0/users/", methods=["GET"])
def get_all_registered_users():
    """ Gets all the registered users """
    users = models.User.query.all()
    if not users:
        return jsonify({"errors": ["No user found"]}), 404

    return jsonify({"users": [current_user.user_details for current_user in users]}), 200


@app.route("/yummy/api/v1.0/users/<id>/", methods=["GET"])
def get_user(id):
    """ Gets user details """
    user_id = Secure.decrypt_user_id(id)
    if user_id:
        user = models.User.query.filter_by(id=user_id).first_or_404()
        return jsonify({"data": user.user_details})
    abort(400)


# error handlers
@app.errorhandler(404)
def not_found_error(error):
    """ Handles errors arising from absence of a resource """
    return make_response(jsonify({"errors": ["Resource Not found"]}), 404)


@app.errorhandler(400)
def bad_request(error):
    """ Handles Bad Request Errors """
    return make_response(jsonify({"errors": ["Request not Understood"]}), 404)


@app.errorhandler(401)
def invalid_authentication_details(error):
    """ Handles Invalid Login credential details """
    return make_response(jsonify({"errors": ["Invalid Login Credentials"]}), 401)


@app.errorhandler(403)
def permission_denied(error):
    """ Handles errors resulting from insufficient permissions to perform a task """
    return make_response(jsonify({"errors": ["You do not have enough permissions to perform this task"]}), 403)


@app.errorhandler(ValidationError)
def handle_validation_failure(error):
    """ Handles failure of validation of sent data, in case some keys are missing """
    return make_response(jsonify({"errors": [error.args[0]]}), 400)


@app.errorhandler(BadSignature)
def handle_invalid_user_ids(error):
    return make_response(jsonify({"errors": ["Request not understood"]}), 400)


@app.errorhandler(models.UserNotFoundError)
def handle_user_not_found_error(error):
    return make_response(jsonify({"errors": [error.args[0]]}), 404)


# handle token errors
@app.errorhandler(TokenExpiredError)
def handle_token_expiration_errors(error):
    return make_response(jsonify({"errors": [error.args[0]]}), 401)


@app.errorhandler(TokenError)
def handle_invalid_token(error):
    return make_response(jsonify({"errors": [error.args[0]]}), 401)
