import json
import requests

from st2actions.runners.pythonrunner import Action


class ScalingAction(Action):

    def run(self, auth_endpoint, username, api_key, webhook):

        # Authenticate with server.

        headers = {'Content-Type': 'application/json'}

        auth_data = {
            'auth': {
                'RAX-KSKEY:apiKeyCredentials': {
                    'username': username,
                    'apiKey': api_key
                }
            }
        }

        response = requests.post(auth_endpoint, headers=headers, data=json.dumps(auth_data))

        if response.status_code != 200:
            self.logger.error('Unable to authenticate.')
            self.logger.error('Status code "%s" returned.' % response.status_code)
            raise Exception(response.text)

        auth_result = response.json()

        if (not auth_result.get('access', None) or
                not auth_result.get('access').get('token', None) or
                not auth_result.get('access').get('token').get('id', None)):
            raise Exception('Unable to find auth token.')

        # Make webhook call to execute the scaling action.

        auth_token = auth_result['access']['token']['id']

        headers = {'X-Auth-Token': auth_token}

        response = requests.post(webhook, headers=headers)

        return response.text
