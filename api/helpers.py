""" The helpers module has helper classes and helper functions i.e.
Secure class handles encrypting and decrypting of tokens and user ids
format_data and format-email methods to ensure storage of uniform data"""
import re

from itsdangerous import URLSafeSerializer,\
                        TimedJSONWebSignatureSerializer as TimedSerializer, SignatureExpired,\
                        base64_decode, base64_encode

from api import app


class TokenExpiredError(SignatureExpired):
    """ An exception raised when a user uses an expired token """
    pass


class TokenError(Exception):
    """ This is an exception raised when a user uses an invalid token """
    pass


class Secure:
    """ Secure class handles basic security operations of the api e.g.
    Generates the token for authentication of api users
    Generates and decrypts public user ids
    """
    __serializer = URLSafeSerializer(
        app.config["SECRET_KEY"], salt="yagshjuegsbkajhsi")
    __timed_serializer = TimedSerializer(
        app.config["SECRET_KEY"], expires_in=app.config["YUMMY_TOKEN_EXPIRY"])

    @staticmethod
    def encrypt_user_id(user_id):
        """ Generates public user ids"""
        return Secure.__serializer.dumps(user_id)

    @staticmethod
    def decrypt_user_id(encrypted_id):
        """Decrypts public user ids"""
        return Secure.__serializer.loads(encrypted_id)

    @staticmethod
    def generate_auth_token(user_id):
        """ Generates an authentication token """
        return base64_encode(Secure.__timed_serializer.dumps({
            "id": user_id
        })).decode("utf-8")

    @staticmethod
    def decrypt_auth_token(token):
        """
        Retrieves information in the access token
        :param token: The token to decrypt
        :return: The dictionary containing the id of the logged in user
        """
        try:
            return Secure.__timed_serializer.loads(
                base64_decode(token.encode("utf-8")))
        except SignatureExpired:
            raise TokenExpiredError("The token has expired")
        except:
            raise TokenError("Invalid Token")


def format_data(data):
    """ Formats data for uniformly saving data in the database """
    return " ".join(str(data).strip().title().split())

def format_email(email):
    """ Formats email to ensure uniform storage of emails in the database """
    return str(email).strip().lower()

def is_invalid_id(the_id):
    """Checks whether a given id is valid"""
    return re.search(r"\D+", the_id)
