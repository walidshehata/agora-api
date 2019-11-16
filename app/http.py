import requests
import logging as log
import urllib3
import json


def http_request(url, headers={}, data=None, method='get', timeout=3, jwt=None, cookie=None, verify_ssl=False):

    if url[:5].lower() == 'https' and not verify_ssl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if jwt:
        headers['Authorization'] = 'JWT {}'.format(jwt)

    if cookie:
        headers['Set-Cookie'] = '{}={}'.format(cookie.name, cookie.value)

    try:
        # https requests apply verify_ssl option
        if url[:5].lower() == 'https':
            if method.lower() == 'get':
                response = requests.get(url, headers=headers, timeout=timeout, verify=verify_ssl)
            elif method.lower() == 'post':
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
