import os


class Config:
    """ Contains configurations common to all environments """
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get(
        "YUMMY_SECRET_KEY", "THhdtgUhhkdldyrhfkfu8369kslo09wjjw")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "YUMMY_DATABASE_URI", "postgresql://postgres:mypassword@127.0.0.1:5432/yummy_recipes")

    SQLALCHEMY_TRACK_MODIFICATIONS = True


class DevelpmentConfig(Config):
    """Has configurations used during development"""
    DEBUG = True


class TestingConfig(Config):
    """ Has configurations used during testing """
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "YUMMY_TEST_DATABASE_URI", "postgresql://postgres:mypassword@127.0.0.1:5432/test_yummy_recipes")


class ProductConfig(Config):
    """ Has configuration for use during Production """
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


configs = {
    "development": DevelpmentConfig,
    "testing": TestingConfig,
    "production": ProductConfig,
    "default": DevelpmentConfig
}
