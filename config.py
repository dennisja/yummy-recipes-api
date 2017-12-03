""" The config module has all api configurations """
import os


class Config:
    """ Contains configurations common to all environments """
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("YUMMY_SECRET_KEY",
                                "THhdtgUhhkdldyrhfkfu8369kslo09wjjw")
    YUMMY_TOKEN_EXPIRY = 604800
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:mypassword@127.0.0.1:5432/yummy_recipes")

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ITEMS_PER_PAGE = os.environ.get("YUMMY_ITEMS_PER_PAGE", 10)
    MAX_ITEMS_PER_PAGE = os.environ.get("YUMMY_MAX_ITEMS_PER_PAGE", 20)


class DevelpmentConfig(Config):
    """Has configurations used during development"""
    DEBUG = True


class TestingConfig(Config):
    """ Has configurations used during testing """
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("YUMMY_TEST_DATABASE_URI",\
    "postgresql://postgres:mypassword@127.0.0.1:5432/test_yummy_recipes")


class ProductConfig(Config):
    """ Has configuration for use during Production """
    pass


CONFIGS = {
    "development": DevelpmentConfig,
    "testing": TestingConfig,
    "production": ProductConfig,
    "default": DevelpmentConfig
}
