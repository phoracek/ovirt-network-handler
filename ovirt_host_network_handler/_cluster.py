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
_NETWORKS = ('apis/ovirt.org/v1alpha1/namespaces/{}/ovirthostnetworks'
             .format(_NAMESPACE))


class Cluster(object):

    def __init__(self, host, token, certs):
        self._host = host
        self._token = token
        self._certs = certs

    def _get(self, resource, name=None):
        if name:
            url = '{}/{}/{}'.format(self._host, resource, name)
        else:
            url = '{}/{}'.format(self._host, resource)

        response = requests.get(
            url, headers={'Authorization': 'Bearer {}'.format(self._token)},
            cert=self._certs, verify=False)
        response.raise_for_status()
        return response.json()

    def get_root(self):
        return self._get('')

    def get_network(self, node_name):
        try:
            return self._get(_NETWORKS, node_name)
        except requests.HTTPError as http_error:
            if http_error.response.status_code == 404:
                return None
            raise

    def _put(self, resource, name, data):
        response = requests.put(
            '{}/{}/{}'.format(self._host, resource, name), json=data,
            headers={'Authorization': 'Bearer {}'.format(self._token)},
            cert=self._certs, verify=False)
        response.raise_for_status()
        return int(response.json()['metadata']['resourceVersion'])

    def _post(self, resource, data):
        response = requests.post(
            '{}/{}'.format(self._host, resource), json=data,
            headers={'Authorization': 'Bearer {}'.format(self._token)},
            cert=self._certs, verify=False)
        response.raise_for_status()
        return int(response.json()['metadata']['resourceVersion'])

    def set_network(self, network):
        name = network['metadata']['name']
        network['metadata'] = {'name': name}
        if self.get_network(name) is None:
            return self._post(_NETWORKS, network)
        else:
            return self._put(_NETWORKS, name, network)

    def _watch(self, resource):
        response = requests.get(
            '{}/{}'.format(self._host, resource), stream=True,
            params={'watch': 'true'},
            headers={'Authorization': 'Bearer {}'.format(self._token)},
            cert=self._certs, verify=False)
        response.raise_for_status()
        for line in response.iter_lines(chunk_size=1):
            if line:
                yield json.loads(line)

    def watch_network(self, node_name):
        for event in self._watch(_NETWORKS):
            if event['object']['metadata']['name'] == node_name:
                yield event
