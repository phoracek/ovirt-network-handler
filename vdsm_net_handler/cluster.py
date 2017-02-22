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
import logging

import requests

_NAMESPACE = 'default'

_NETWORKS = ('apis/ovirt.org/v1alpha1/namespaces/{}/vdsmnetworks'
             .format(_NAMESPACE))
_BONDINGS = ('apis/ovirt.org/v1alpha1/namespaces/{}/vdsmbondings'
             .format(_NAMESPACE))
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

    def get_networks(self):
        logging.error('request get nets')
        return self._get(_NETWORKS)['items']

    def get_bondings(self):
        logging.error('request get bonds')
        return self._get(_BONDINGS)['items']

    def get_attachment(self, node_name):
        logging.error('request get attachment')
        return next((attachment
                     for attachment in self._get(_ATTACHMENTS)['items']
                     if attachment['metadata']['name'] == node_name),
                    None)

    def _put(self, resource, name, data):
        response = requests.put(
            '{}/{}/{}'.format(self._host, resource, name), json=data,
            headers={'Authorization': 'Bearer {}'.format(self._token)},
            verify=False)
        response.raise_for_status()

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
        self._put(resource, name, _doc)

    def put_network_state(self, doc, status, reason='', message='',
                          save_spec_to_state=False):
        self._put_state(
            _NETWORKS, doc, status, reason, message, save_spec_to_state)

    def put_bonding_state(self, doc, status, reason='', message='',
                          save_spec_to_state=False):
        self._put_state(
            _BONDINGS, doc, status, reason, message, save_spec_to_state)

    def put_attachment_state(self, doc, status, reason='', message='',
                             save_spec_to_state=False):
        self._put_state(
            _ATTACHMENTS, doc, status, reason, message, save_spec_to_state)

    # NOTE: not used yet
    def watch(self, resource):
        response = requests.get(
            '{}/{}?watch=true'.format(self._host, resource), stream=True,
            headers={'Authorization': 'Bearer {}'.format(self._token)},
            verify=False)
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                yield json.loads(decoded_line)
