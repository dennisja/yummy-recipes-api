"""This is the errors module
It houses all error handlers of the api """

from flask import make_response, jsonify
from itsdangerous import BadSignature

from api import app, models
from api.validator import ValidationError
from api.helpers import TokenError, TokenExpiredError


# error handlers
@app.errorhandler(404)
def not_found_error(error):
    """ Handles errors arising from absence of a resource """
    return make_response(jsonify({"errors": ["Resource Not found"]}), 404)


@app.errorhandler(400)
@app.errorhandler(BadSignature)
def bad_request(error):
    """ Handles Bad Request Errors """
    return make_response(jsonify({"errors": ["Request not Understood"]}), 400)


@app.errorhandler(401)
def invalid_authentication_details(error):
    """ Handles Invalid Login credential details """
    return make_response(jsonify({"errors": ["Invalid Login Credentials"]}), 401)


@app.errorhandler(403)
def permission_denied(error):
    """ Handles errors resulting from insufficient permissions to perform a task """
    return make_response(jsonify({
        "errors": ["You do not have enough permissions to perform this task"]}), 403)


@app.errorhandler(ValidationError)
def handle_validation_failure(error):
    """ Handles failure of validation of sent data, in case some keys are missing """
    return make_response(jsonify({"errors": [error.args[0]]}), 400)


@app.errorhandler(models.UserNotFoundError)
def handle_user_not_found_error(error):
    """ Handles user not found errors """
    return make_response(jsonify({"errors": [error.args[0]]}), 404)


# handle token errors
@app.errorhandler(TokenExpiredError)
@app.errorhandler(TokenError)
def handle_token_errors(error):
    """ Handles authentication token errors"""
    return make_response(jsonify({"errors": [error.args[0]]}), 401)


@app.errorhandler(500)
def handle_server_error(error):
    """ Handles internal server errors"""
    return make_response(jsonify({
        "errors": ["Server encountered an error. Please try again later"]}), 500)


@app.errorhandler(405)
def handle_method_not_allowed(error):
    """ Handles method not allowed error """
    return make_response(jsonify({
        "errors":[
            "The method you are trying on the end po\
            int is not allowed. Please try with a correct method",
            ]
    }), 405)
