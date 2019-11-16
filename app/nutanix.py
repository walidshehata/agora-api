from base64 import b64encode
import logging as log

from .http import http_request
from . import db
from .models import User, load_user


class PrismClient(object):

    config = None

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.config = app.config

    def authenticate(self, username, password):
        domain = self.config['DOMAIN']
        auth_url = 'https://{}:{}/api/nutanix/v3/users/me'.format(self.config['PC_HOST'], self.config['PC_PORT'])
        encoded_credentials = b64encode(bytes(f'{username}@{domain}:{password}',
                                              encoding='ascii')).decode('ascii')
        auth_header = f'Basic {encoded_credentials}'
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
                   'Authorization': f'{auth_header}', 'cache-control': 'no-cache'}

        response = http_request(url=auth_url, headers=headers, verify_ssl=self.config['VERIFY_SSL'],
                                timeout=self.config['HTTP_TIMEOUT'])

        try:
            data = response.json()
            if response.status_code == 200 and 'access_token' in data:
                user = load_user(username)
                if user:
                    user.cookie = data['access_token']
                else:
                    tenant_id = None
                    tenant_uuid = None
                    for project in data['status']['resources']['projects_reference_list']:
                        if project['name'][:9] == 'CUSTOMER-':
                            tenant_id = project['name'][9:]
                            tenant_uuid = project['uuid']
                    user = User(username=username, display_name=data['status']['resources']['display_name'],
                                uuid=data['metadata']['uuid'], tenant_uuid=tenant_uuid, tenant_id=tenant_id)

                db.session.add(user)
                db.session.commit()
            else:
                log.info('Error authenticating user: {}, bad username or password'.format(username))
                return None
        except KeyError:
            return None



