# Copyright 2017 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

import requests

_NAMESPACE = 'default'
_ATTACHMENTS = ('apis/ovirt.org/v1alpha1/namespaces/{}/vdsmnetworkattachments'
                .format(_NAMESPACE))


class Cluster(object):

    def __init__(self, host, token):
        self._host = host
        self._token = token

    def _get(self, resource):
        response = requests.get(
            '{}/{}'.format(self._host, resource),
            headers={'Authorization': 'Bearer {}'.format(self._token)},
            verify=False)
        response.raise_for_status()
        return response.json()

    def get_root(self):
        return self._get('')

    def get_attachment(self, name):
        return next((attachment
                     for attachment in self._get(_ATTACHMENTS)['items']
                     if attachment['metadata']['name'] == name),
                    None)

    def _put(self, resource, name, data):
        response = requests.put(
            '{}/{}/{}'.format(self._host, resource, name), json=data,
            headers={'Authorization': 'Bearer {}'.format(self._token)},
            verify=False)
        response.raise_for_status()
        return response.json()['metadata']['resourceVersion']

    def _put_state(self, resource, doc, status, reason='', message='',
                   save_spec_to_state=False):
        name = doc['metadata']['name']
        _doc = {
            'metadata': {'name': name},
            'spec': doc['spec'],
            'state': (doc['spec'] if save_spec_to_state
                      else doc.get('state', {}))
        }
        _doc['state']['status'] = {
            status: {'reason': reason, 'message': message}}
        return self._put(resource, name, _doc)

    def put_attachment_state(self, doc, status, reason='', message='',
                             save_spec_to_state=False):
        return self._put_state(_ATTACHMENTS, doc, status, reason, message,
                               save_spec_to_state)

    def _post(self, resource, data):
        response = requests.post(
            '{}/{}'.format(self._host, resource), json=data,
            headers={'Authorization': 'Bearer {}'.format(self._token)},
            verify=False)
        response.raise_for_status()
        return response.json()['metadata']['resourceVersion']

    def post_attachment(self, doc):
        return self._post(_ATTACHMENTS, doc)

    def _watch(self, resource):
        response = requests.get(
            '{}/{}'.format(self._host, resource), stream=True,
            params={'watch': 'true'},
            headers={'Authorization': 'Bearer {}'.format(self._token)},
            verify=False)
        response.raise_for_status()
        for line in response.iter_lines(chunk_size=1):
            if line:
                yield json.loads(line)

    def watch_attachment(self, name):
        for attachment in self._watch(_ATTACHMENTS):
            if attachment['object']['metadata']['name'] == name:
                yield attachment
