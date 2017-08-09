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
import os

import requests

_SERVICE_SECRETS = '/var/run/secrets/kubernetes.io/serviceaccount'
_TOKEN_FILE = os.path.join(_SERVICE_SECRETS, 'token')
_CERT_FILE = os.path.join(_SERVICE_SECRETS, 'service-ca.crt')

_RESOURCE_PREFIX = 'apis/ovirt.org/v1alpha1/namespaces/{}/'
_NETWORK_ATTACHMENT_RESOURCE = _RESOURCE_PREFIX + 'ovirtnodenetworkattachments'
_NETWORK_INFO_RESOURCE = _RESOURCE_PREFIX + 'ovirtnodenetworkinfos'


class Cluster(object):

    def __init__(self):
        self._host = _get_host()
        self._session = requests.Session()
        self._session.headers.update(
            {'Authorization': 'Bearer {}'.format(_get_token())}
        )
        self._session.verify = _CERT_FILE

    def get(self, resource, name=None):
        if name is None:
            url = '{}/{}'.format(self._host, resource)
        else:
            url = '{}/{}/{}'.format(self._host, resource, name)
        response = self._session.get(url)
        response.raise_for_status()
        return response.json()

    def watch(self, resource):
        response = self._session.get(
            '{}/{}'.format(self._host, resource),
            stream=True, params={'watch': 'true'}
        )
        response.raise_for_status()
        for line in response.iter_lines(chunk_size=1):
            if line:
                yield json.loads(line)

    def put(self, resource, name, data):
        response = self._session.put(
            '{}/{}/{}'.format(self._host, resource, name), json=data
        )
        response.raise_for_status()
        return int(response.json()['metadata']['resourceVersion'])

    def post(self, resource, data):
        response = self._session.post(
            '{}/{}'.format(self._host, resource), json=data
        )
        response.raise_for_status()
        return int(response.json()['metadata']['resourceVersion'])


def _get_host():
    return 'https://{}:{}'.format(
        os.environ['KUBERNETES_SERVICE_HOST'],
        os.environ['KUBERNETES_PORT_443_TCP_PORT']
    )


def _get_token():
    with open(_TOKEN_FILE) as token_file:
        return token_file.read()


class NodeNetworkAttachmentCluster(Cluster):

    def __init__(self, node_name, project_name):
        super(NodeNetworkAttachmentCluster, self).__init__()
        self._node_name = node_name
        self._resource = _NETWORK_ATTACHMENT_RESOURCE.format(project_name)

    def get_network_attachment(self):
        try:
            return self.get(self._resource, self._node_name)
        except requests.HTTPError as http_error:
            if http_error.response.status_code == 404:
                return None
            raise

    def watch_network_attachment(self):
        for event in self.watch(self._resource):
            if event['object']['metadata']['name'] == self._node_name:
                yield event

    def set_network_attachment(self, network_attachment):
        name = network_attachment['metadata']['name']
        network_attachment['metadata'] = {'name': name}
        if self.get_network_attachment() is None:
            return self.post(self._resource, network_attachment)
        else:
            return self.put(self._resource, name, network_attachment)


class NodeNetworkInfoCluster(Cluster):

    def __init__(self, node_name, project_name):
        super(NodeNetworkInfoCluster, self).__init__()
        self._node_name = node_name
        self._resource = _NETWORK_INFO_RESOURCE.format(project_name)

    def set_network_info(self, network_info):
        name = network_info['metadata']['name']
        network_info['metadata'] = {'name': name}
        if self._get_network_info() is None:
            return self.post(self._resource, network_info)
        else:
            return self.put(self._resource, name, network_info)

    def _get_network_info(self):
        try:
            return self.get(self._resource, self._node_name)
        except requests.HTTPError as http_error:
            if http_error.response.status_code == 404:
                return None
            raise
