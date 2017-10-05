from api import app, db
from api import models
from api.validator import Validate
from flask import make_response, jsonify, abort, request, url_for
import json


@app.route("/yummy/api/v1.0/auth/register/", methods=["POST"])
def register_user():
    """ Registers a yummy recipes user """
    if not request.json:
        abort(400)

    # validate user data
    data_validator = Validate()
    validation_errors = data_validator.validate_data(request.json, {
        "firstname": {
            "required": True
        },
        "lastname": {
            "required": True
        },
        "email": {
            "required":True,
            "email":True,
            "min": 8,
            "max": 100
        },
        "password": {
            "required": True,
            "min": 8,
            "max": 20
        }
    })

    # check if errors occured
    if validation_errors:
        return jsonify({"errors": validation_errors })

    # check if user already exists
    existing_user = models.User.query.filter_by(email=request.json["email"]).first()
    if existing_user:
        return jsonify({"errors": ["Email address already in use"]})
    
    # register the user
    user = models.User(request.json["email"], request.json["firstname"],
                       request.json["lastname"], request.json["password"])
    db.session.add(user)
    db.session.commit()

    return jsonify({"messages": ["You have been successfully registered and you can now login"]})


@app.errorhandler(404)
def not_found_error(error):
    """ Handles errors arising from absence of a resource """
    return make_response(jsonify({"errors": ["Resource Not found"]}))


@app.errorhandler(400)
def bad_request(error):
    """ Handles Bad Request Errors """
    return make_response(jsonify({"errors": ["Request not Understood"]}))
