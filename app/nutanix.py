import logging as log

from .http import http_request
from . import db
from .models import User


class PrismClient(object):

    config = None
    dir_uuid = None
    agora_uuid = None

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.config = app.config

        # query PC to get the uuid of Directory service
        # TODO: no error handling if no Directory service defined (essential for agora to work)
        cred = {'username': self.config['PC_USERNAME'], 'password': self.config['PC_PASSWORD']}

        # get directory service uuid
        api_url = 'api/nutanix/v3/directory_services/list'
        data = {'filter': '', 'kind': 'directory_service'}
        response = http_request(api_url, cred=cred, method='POST', data=data)

        if response.status_code == 200:
            dir_list = response.json()
            for item in dir_list['entities']:
                if item['spec']['resources']['domain_name'] == self.config['DOMAIN']:
                    self.dir_uuid = item['metadata']['uuid']

        # get agora Calm app uuid
        # TODO: no handling if no app deployment found
        api_url = 'api/nutanix/v3/apps/list'
        data = {'filter': f'name=={self.config["AGORA_APP_NAME"]}', 'kind': 'app'}
        response = http_request(api_url, cred=cred, method='POST', data=data)

        if response.status_code == 200:
            app_list = response.json()
            for item in app_list['entities']:
                self.agora_uuid = item['metadata']['uuid']

    def get_user_info(self, username):

        user = {'mail': None, 'company': None, 'username': None, 'mobile': None}
        domain = self.config['DOMAIN']
        dir_uuid = self.dir_uuid
        cred = {'username': self.config['PC_USERNAME'], 'password': self.config['PC_PASSWORD']}
        dir_search_url = f'api/nutanix/v3/directory_services/{dir_uuid}/search'
        data = {
            'query': f'{username}@{domain}',
            'returned_attribute_list': ['company', 'mail', 'description', 'userPrincipalName', 'mobile'],
            'searched_attribute_list': ['userPrincipalName'],
            'is_wildcard_search': False
        }

        if dir_uuid:
            # checking if dir_uuid is set, can be safely removed if dir handled proper in init_app
            response = http_request(url=dir_search_url, method='POST', data=data, cred=cred)
            if response.status_code == 200:
                result = response.json()
                # TODO: just check if the result is 1 only, there should be only one. No error raised.
                #  Same goes for attribute_list and value_list in result
                if len(result['search_result_list']) == 1:
                    for item in result['search_result_list'][0]['attribute_list']:
                        if item['name'] == 'mail':
                            user['mail'] = item['value_list'][0]
                        elif item['name'] == 'company':
                            user['company'] = item['value_list'][0]
                        elif item['name'] == 'userPrincipalName':
                            user['username'] = item['value_list'][0]
                        elif item['name'] == 'mobile':
                            user['mobile'] = item['value_list'][0]

        return user

    def authenticate(self, username, password):
        auth_url = 'api/nutanix/v3/users/me'
        domain = self.config['DOMAIN']
        cred = {'username': f'{username}@{domain}', 'password': password}
        response = http_request(url=auth_url, cred=cred)
        try:
            data = response.json()
            if response.status_code == 200:

                session_cookie = None
                for cookie in response.cookies:
                    if cookie.name == 'NTNX_IGW_SESSION':
                        session_cookie = cookie.value

                user = User.load_user(username)

                if user:
                    user.cookie = session_cookie
                else:
                    tenant_id = None
                    tenant_uuid = None
                    # extract tenant ID from the project name
                    # TODO: assuming user is member of single project, no handling if multiple projects assigned
                    for project in data['status']['resources']['projects_reference_list']:
                        if project['name'][:7].upper() == 'TENANT-':
                            tenant_id = project['name'][7:].upper()
                            tenant_uuid = project['uuid']

                    # get extra user info (mail and company) using directory search
                    user_extra_info = self.get_user_info(username)
                    user = User(id=username,
                                display_name=data['status']['resources']['display_name'],
                                uuid=data['metadata']['uuid'],
                                tenant_id=tenant_id,
                                tenant_uuid=tenant_uuid,
                                cookie=session_cookie,
                                mail=user_extra_info['mail'],
                                company=user_extra_info['company'],
                                mobile=user_extra_info['mobile'])

                db.session.add(user)
                db.session.commit()
                return user
            else:
                log.info('Error authenticating user: {}, bad username or password'.format(username))
                return None
        except AttributeError:
            return None

    def onboard_tenant(self, username, password, company, mail, firstname, lastname, mobile):
        cred = {'username': self.config['PC_USERNAME'], 'password': self.config['PC_PASSWORD']}
        api_url = f'api/nutanix/v3/apps/{self.agora_uuid}/actions/run'
        args = [
            {'name': 'USERID', 'value': username},
            {'name': 'PASSWORD', 'value': password},
            {'name': 'FIRST_NAME', 'value': firstname},
            {'name': 'LAST_NAME', 'value': lastname},
            {'name': 'EMAIL', 'value': mail},
            {'name': 'COMPANY', 'value': company},
            {'name': 'MOBILE', 'value': mobile}
        ]
        data = {
            'args': args,
            'name': self.config['ONBOARD_ACTION_NAME']
        }

        # check if username already there
        check_user = self.get_user_info(username)
        if check_user['username']:
            return 'Username already exists in the system', 400
        else:
            response = http_request(api_url, cred=cred, method='POST', data=data)
            if response.status_code == 200:
                task_uuid = response.json()
                return task_uuid['runlog_uuid'], 200
        return 'Undefined error', 400

