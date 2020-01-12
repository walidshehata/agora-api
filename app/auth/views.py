from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from . import auth
from .. import prism
from ..models import User


# login API endpoint
@auth.route('/', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({'msg': 'Missing JSON in request'}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({'msg': 'Missing username parameter'}), 400
    if not password:
        return jsonify({'msg': 'Missing password parameter'}), 400

    user = prism.authenticate(username, password)
    if user:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'msg': 'Bad username or password'}), 401


@auth.route('/me', methods=['GET'])
@jwt_required
def current_user():
    user_id = get_jwt_identity()
    return jsonify(User.load_user(user_id).dict()), 200


@auth.route('/onboard', methods=['POST'])
def onboard_new_customer():

    if not request.is_json:
        return jsonify({'msg': 'Missing JSON in request'}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    company = request.json.get('company', None)
    mail = request.json.get('mail', None)
    firstname = request.json.get('firstname', None)
    lastname = request.json.get('lastname', None)
    mobile = request.json.get('mobile', None)
    print(request.json)

    if not username and password and company and mail and firstname and lastname and mobile:
        return jsonify({'msg': 'Missing new user parameter'}), 400

    result, status_code = prism.onboard_tenant(username, password, company, mail, firstname, lastname, mobile)

    return jsonify({'msg': result}), status_code

