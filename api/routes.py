from api import app, models
from api.helpers import Secure
from api.validator import ValidationError
from flask import make_response, jsonify, abort, request, url_for
from itsdangerous import BadSignature


@app.route("/yummy/api/v1.0/auth/register/", methods=["POST"])
def register_user():
    """ Registers a yummy recipes user """
    if not request.json:
        abort(400)

    # validate the user
    validation_errors = models.User.validate_user(request.json)

    # check if errors occured
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


@app.route("/yummy/api/v1.0/users/<id>", methods=["GET"])
def get_user(id):
    """ Gets user details """
    user_id = Secure.decrypt_user_id(id)
    if user_id:
        user = models.User.query.filter_by(id=user_id).first_or_404()
        return jsonify({"data": user.user_details})
    abort(400)


@app.errorhandler(404)
def not_found_error(error):
    """ Handles errors arising from absence of a resource """
    return make_response(jsonify({"errors": ["Resource Not found"]}), 404)


@app.errorhandler(400)
def bad_request(error):
    """ Handles Bad Request Errors """
    return make_response(jsonify({"errors": ["Request not Understood"]}), 404)


@app.errorhandler(ValidationError)
def handle_validation_failure(error):
    """ Handles failure of validation of sent data, in case some keys are missing """
    return make_response(jsonify({"errors": [error.args[0]]}), 422)


@app.errorhandler(BadSignature)
def handle_invalid_user_ids(error):
    return make_response(jsonify({"errors": ["Request not understood"]}), 400)
