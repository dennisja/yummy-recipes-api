from itsdangerous import URLSafeSerializer

class Secure:
    serializer = URLSafeSerializer("henhsecretajgkeyF682b2agX", salt="yagshjuegsbkajhsi")
    @staticmethod
    def encrypt_user_id(id):
        return Secure.serializer.dumps(id)


    @staticmethod
    def decrypt_user_id(encrypted_id):
        return Secure.serializer.loads(encrypted_id)