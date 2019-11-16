from base64 import b64encode
import logging as log
from . import db
from config import Config
from .http import http_request


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(40), primary_key=True)
    uuid = db.Column(db.String(36), unique=True)
    display_name = db.Column(db.String(60), default=None)
    tenant_id = db.Column(db.String(16), default=None)
    tenant_uuid = db.Column(db.String(36), default=None)
    cookie = db.Column(db.String(), default=None)

    def __repr__(self):
        return {
            'username': self.id,
            'display_name': self.display_name,
            'uuid': self.uuid,
            'cookie': self.cookie
        }


def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


def identify(payload):
    return User.query.filter(id=payload['identity']).first()
    # return 'hello'


def authenticate(username, password):
    domain = Config.DOMAIN
    auth_url = 'https://{}:{}/api/nutanix/v3/users/me'.format(Config.PC_HOST, Config.PC_PORT)
    encoded_credentials = b64encode(bytes(f'{username}@{domain}:{password}',
                                          encoding='ascii')).decode('ascii')
    auth_header = f'Basic {encoded_credentials}'
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
               'Authorization': f'{auth_header}', 'cache-control': 'no-cache'}

    response = http_request(url=auth_url, headers=headers, verify_ssl=Config.VERIFY_SSL,
                            timeout=Config.HTTP_TIMEOUT)
    try:
        data = response.json()
        if response.status_code == 200:

            session_cookie = None
            for cookie in response.cookies:
                if cookie.name == 'NTNX_IGW_SESSION':
                    session_cookie = cookie.value

            user = load_user(username)

            if user:
                user.cookie = session_cookie
            else:
                tenant_id = None
                tenant_uuid = None
                for project in data['status']['resources']['projects_reference_list']:
                    if project['name'][:9] == 'CUSTOMER-':
                        tenant_id = project['name'][9:]
                        tenant_uuid = project['uuid']
                user = User(id=username, display_name=data['status']['resources']['display_name'],
                            uuid=data['metadata']['uuid'], tenant_uuid=tenant_uuid, tenant_id=tenant_id,
                            cookie=session_cookie)

            db.session.add(user)
            db.session.commit()
            return user
        else:
            log.info('Error authenticating user: {}, bad username or password'.format(username))
            return None
    except AttributeError:
        return None
