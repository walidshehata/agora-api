from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from config import config

db = SQLAlchemy()
jwt = JWTManager()

from .nutanix import PrismClient
prism = PrismClient()

from .models import User, authenticate, identify, load_user


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    prism.init_app(app)

    @app.route('/')
    def index():
        result = []
        for user in db.session.query(User).all():
            result.append(user.__repr__())
        return jsonify(result)

    @app.route('/auth', methods=['POST'])
    def login():
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        username = request.json.get('username', None)
        password = request.json.get('password', None)
        if not username:
            return jsonify({"msg": "Missing username parameter"}), 400
        if not password:
            return jsonify({"msg": "Missing password parameter"}), 400

        user = authenticate(username, password)
        if user:
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"msg": "Bad username or password"}), 401

    @app.route('/me')
    @jwt_required
    def current_user():
        user = get_jwt_identity()
        # return jsonify(logged_in_as=user), 200
        return jsonify(load_user(user).json()), 200

    with app.app_context():
        db.create_all()

    return app
