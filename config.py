import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
    PC_HOST = os.environ.get('PC_HOST', '10.38.14.9')
    PC_PORT = os.environ.get('PC_PORT', '9440')
    DOMAIN = os.environ.get('DOMAIN', 'demo.lan')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    VERIFY_SSL = False
    HTTPS = True
    HTTP_TIMEOUT = 3
    PC_USERNAME = 'admin'
    PC_PASSWORD = 'nx2Tech911!'
    AGORA_APP_NAME = 'SYS-AGORA'
    ONBOARD_ACTION_NAME = 'onboard_new_customer'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI', 'sqlite:///')


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI', 'sqlite:///')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URI', 'sqlite:///')
    VERIFY_SSL = True


config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}