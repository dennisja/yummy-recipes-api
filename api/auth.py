"""This is the auth module
It has end points for user authentication """
from flask import request, jsonify, abort

from api import app, models
from api.validator import ValidateUser
from api.helpers import Secure


@app.route("/yummy/api/v1.0/auth/register/", methods=["POST"])
def register_user():
    """ Registers a yummy recipes user """
    if not request.get_json():
        abort(400)

    request_data = request.get_json()
    # validate the user
    validation_errors = ValidateUser.validate_user_on_reg(request_data)

    # check if errors occurred
    if validation_errors:
        return jsonify({"errors": validation_errors}), 422

    # check if user already exists
    existing_user = models.User.query.filter_by(
        email=request_data["email"]).first()
    if existing_user:
        return jsonify({"errors": [f"Email address \'{request_data['email']}\' already in use"]}
                      ), 422

    # register the user
    user = models.User(request_data["email"], request_data["firstname"],
                       request_data["lastname"], request_data["password"])
    user.save_user()

    return jsonify(
        {"messages": ["You have been successfully registered and you can now login"],
         "data": user.user_details}), 201


@app.route("/yummy/api/v1.0/auth/login/", methods=["POST"])
def login_user():
    """ The end point is used to login a user """
    auth_details = request.authorization
    # check whether authorization details are supplied
    if not auth_details or "username" not in auth_details or "password" not in auth_details:
        return jsonify({"errors": ["Missing login credentials"]}), 400
    # validate sent details
    validation_errors = ValidateUser.validate_user_login(auth_details)
    if validation_errors:
        return jsonify({"errors": validation_errors}), 401, {
            "WWW-Authenticate": "Basic realm='Invalid login credentials'"}

    # check if a user exists
    user = models.User.query.filter_by(email=auth_details["username"]).first()
    if not user:
        raise models.UserNotFoundError(
            f"Email '{auth_details['username']}' is not yet registered")

    # if user password is correct
    if user.verify_password(auth_details["password"]):
        access_token = Secure.generate_auth_token(user.id)
        return jsonify({"message": "Successfully logged in", "token": access_token}), 200
        # generate and return the token

    return jsonify({"errors": ["Invalid email and password combination"]}), 401, {
        "WWW-Authenticate": "Basic realm='Invalid email and password combination'"}
