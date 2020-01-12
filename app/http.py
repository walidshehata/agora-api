import requests
import logging as log
import urllib3
import json
from base64 import b64encode

from config import Config


def http_request(url, headers={}, data=None, method='get',
                 cred=None, token=None, cookie=None):

    https = Config.HTTPS
    timeout = Config.HTTP_TIMEOUT
    verify_ssl = Config.VERIFY_SSL
    host = Config.PC_HOST
    port = Config.PC_PORT

    if https:
        url = f'https://{host}:{port}/{url}'
    else:
        url = f'http://{host}:{port}/{url}'

    if https and not verify_ssl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if cred:
        username = cred.get('username')
        password = cred.get('password')
        encoded_credentials = b64encode(bytes(f'{username}:{password}', encoding='ascii')).decode('ascii')
        headers['Authorization'] = f'Basic {encoded_credentials}'
    elif token:
        headers['Authorization'] = 'Bearer {}'.format(token)

    if cookie:
        headers['Set-Cookie'] = '{}={}'.format(cookie.name, cookie.value)

    try:
        # https requests apply verify_ssl option
        if https:
            if method.lower() == 'get':
                response = requests.get(url, headers=headers, timeout=timeout, verify=verify_ssl)
            elif method.lower() == 'post':
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, data=json.dumps(data), headers=headers, timeout=timeout,
                                         verify=verify_ssl)
            else:
                response = None
        else:
            # http request, so remove verify_ssl option else error is raised by requests lib
            if method.lower() == 'get':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method.lower() == 'post':
                response = requests.post(url, data=json.dumps(data), headers=headers, timeout=timeout)
            else:
                response = None
    except requests.ConnectTimeout:
        log.error('Connection time out while connecting to {}. '
                  'Please check connectivity with backend'.format(url))
        return False
    except requests.ConnectionError:
        log.error('Connection error while connecting to {}. '
                  'Please check connectivity with backend.'.format(url))
        return False
    except requests.HTTPError:
        log.error('Connection error while connecting to {}. '
                  'Please check connectivity with backend.'.format(url))
        return False
    except Exception as error:
        log.error('An unexpected error while connecting to {} - '
                  'Exception: {}'.format(url, error.__class__.__name__))
        return False

    return response
