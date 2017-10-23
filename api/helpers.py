from itsdangerous import URLSafeSerializer, TimedJSONWebSignatureSerializer as TimedSerializer, SignatureExpired, \
    base64_decode, base64_encode
from api import app


class TokenExpiredError(SignatureExpired):
    pass


class TokenError(Exception):
    pass


class Secure:
    serializer = URLSafeSerializer(app.config["SECRET_KEY"], salt="yagshjuegsbkajhsi")
    __timed_serilizer = TimedSerializer(app.config["SECRET_KEY"], expires_in=3600)

    @staticmethod
    def encrypt_user_id(id):
        return Secure.serializer.dumps(id)

    @staticmethod
    def decrypt_user_id(encrypted_id):
        return Secure.serializer.loads(encrypted_id)

    @staticmethod
    def generate_auth_token(user_id):
        return base64_encode(Secure.__timed_serilizer.dumps({"id": user_id})).decode("utf-8")

    @staticmethod
    def decrypt_auth_token(token):
        """
        Retrieves information in the access token
        :param token: The token to decrypt
        :return: The dictionary containing the id of the logged in user
        """
        try:
            return Secure.__timed_serilizer.loads(base64_decode(token.encode("utf-8")))
        except SignatureExpired:
            raise TokenExpiredError("The token has expired")
        except:
            raise TokenError("Invalid Token")
