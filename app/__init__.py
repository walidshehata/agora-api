from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import config

db = SQLAlchemy()
jwt = JWTManager()

from .nutanix import PrismClient
prism = PrismClient()

from .models import User


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    prism.init_app(app)

    # temporary API call to display all logged users in memory
    @app.route('/')
    def index():
        result = []
        for user in db.session.query(User).all():
            result.append(user.dict())
        return jsonify(result)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    with app.app_context():
        db.create_all()

    return app
