from flask import Flask, jsonify
from flask_jwt import JWT, jwt_required, current_identity

from lib.config import CONFIG
from lib.nutanix import Prism
from lib.authenticate import authenticate, identity
from lib.users import user_list

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
prism = Prism(pc_host=CONFIG.pc_host, pc_port=CONFIG.pc_port, ignore_ssl=CONFIG.ignore_ssl)
jwt = JWT(app, authenticate, identity)


@app.route('/')
def get_all():
    global user_list
    result = []
    for user in user_list:
        result.append(user.get())
    return jsonify(result)


@app.route('/secure')
@jwt_required()
def secure():
    some = current_identity
    return jsonify(some.get())


if __name__ == '__main__':
    app.run(port='6000')
