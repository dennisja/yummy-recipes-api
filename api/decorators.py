from functools import wraps
from api.helpers import Secure
from flask import request, jsonify
from api.models import User


def json_data_required(decorated_func):
    """ Ensures that json data is available in the request """

    @wraps(decorated_func)
    def wrapper(*args, **kwargs):
        if not request.json:
            return jsonify(
                {"errors": ["Request body is absent, Make sure you are sending json data and try again"]}), 400
        return decorated_func(*args, **kwargs)

    return wrapper


def auth_token_required(decorated_func):
    """ Protects access certain routes if a valid token is not supplied """

    @wraps(decorated_func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("x-access-token", default=None)

        if not token:
            return jsonify({"errors": ["The access token is required"]}), 401

        # grab user id from the token
        user_id = Secure.decrypt_auth_token(token)["id"]
        current_user = User.query.filter_by(id=user_id).first()

        if not current_user:
            return jsonify({"errors": "User not found"}), 404

        # call decorated function passing the current user object as the first argument
        return decorated_func(current_user, *args, **kwargs)

    return wrapper
