from api import app, db
from api import models
from api.validator import ValidationError
from flask import make_response, jsonify, abort, request, url_for
import json


@app.route("/yummy/api/v1.0/auth/register/", methods=["POST"])
def register_user():
    """ Registers a yummy recipes user """
    if not request.json:
        abort(400)

    # validate the user
    validation_errors = models.User.validate_user(request.json)

    # check if errors occured
    if validation_errors:
        return jsonify({"errors": validation_errors })

    # check if user already exists
    existing_user = models.User.query.filter_by(email=request.json["email"]).first()
    if existing_user:
        return jsonify({"errors": ["Email address '{}' already in use".format(request.json["email"])]})

    # register the user
    user = models.User(request.json["email"], request.json["firstname"],
                       request.json["lastname"], request.json["password"])
    user.save_user()

    return jsonify({"messages": ["You have been successfully registered and you can now login"], "data":user.user_details})

@app.route("/yummy/api/v1.0/users/<int:id>",methods=["GET"])
def get_user(id):
    """ Gets user details """
    user = models.User.query.filter_by(id=id).first_or_404()
    return jsonify({"data":user.user_details})

@app.errorhandler(404)
def not_found_error(error):
    """ Handles errors arising from absence of a resource """
    response = jsonify({"errors": ["Resource Not found"]})
    response.status_code = 404
    return response


@app.errorhandler(400)
def bad_request(error):
    """ Handles Bad Request Errors """
    response = jsonify({"errors": ["Request not Understood"]})
    response.status_code = 400
    return response

@app.errorhandler(ValidationError)
def handle_validation_failure(error):
    """ Handles failure of validation of sent data, in case some keys are missing """
    response = jsonify({"errors":[error.args[0]]})
    response.status_code = 422
    return response