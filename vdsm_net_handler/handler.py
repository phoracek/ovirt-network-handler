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

import copy
import logging
import os
import random
import time
import traceback

import six

from . import configurator, cluster, validation

try:
    _basestring = basestring
except NameError:  # Python 3
    _basestring = str

_TOKEN_FILE = '/var/run/secrets/kubernetes.io/serviceaccount/token'


class Handler(object):

    def __init__(self):
        logging.info('Initializing handler.')
        self._node_name = os.environ['NODE_NAME']
        self._cluster = cluster.Cluster(
            'https://{}:{}'.format(os.environ['KUBERNETES_SERVICE_HOST'],
                                   os.environ['KUBERNETES_PORT_443_TCP_PORT']),
            _get_token())
        configurator.init()

    def setup(self):
        logging.info('Handler setup was triggered.')
        networks = self._cluster.get_networks()
        bondings = self._cluster.get_bondings()
        logging.debug('Received networks: %s', networks)
        logging.debug('Received bondings: %s', bondings)

        for doc in networks:
            self._validate_network(doc)

        for doc in bondings:
            self._validate_bonding(doc)

        attachment = self._cluster.get_attachment(self._node_name)
        if attachment is None:
            logging.debug('There is not attachment to process.')
            return

        attachment_body = self._validate_attachment(attachment)
        if attachment_body is None:
            return

        desired_networks, desired_bondings = self._merge(
            attachment, attachment_body, networks, bondings)

        self._setup(attachment, desired_networks, desired_bondings)

    def _validate_network(self, doc):
        try:
            validation.validate_network(doc)
        except validation.ValidationError:
            logging.warning('Invalid network specification: %s', doc,
                            exc_info=True)
            self._cluster.put_network_state(
                doc, 'Failed', 'ValidationFailed', traceback.format_exc())
        else:
            self._cluster.put_network_state(
                doc, 'Success', save_spec_to_state=True)

    def _validate_bonding(self, doc):
        try:
            validation.validate_bonding(doc)
        except validation.ValidationError:
            logging.warning('Invalid bonding specification: %s', doc,
                            exc_info=True)
            self._cluster.put_bonding_state(
                doc, 'Failed', 'ValidationFailed', traceback.format_exc())
        else:
            self._cluster.put_bonding_state(
                doc, 'Success', save_spec_to_state=True)

    def _validate_attachment(self, doc):
        try:
            validation.validate_attachment(doc)
        except validation.ValidationError:
            logging.warning('Invalid attachment specification: %s', doc)
            self._cluster.put_attachment_state(
                doc, 'Failed', 'ValidationFailed',
                traceback.format_exc())
            if 'state' in doc:
                attachment_body = doc['state']
                attachment_body.pop('status')
            else:
                attachment_body = None
        else:
            attachment_body = doc['spec']
        return attachment_body

    def _setup(self, attachment, desired_networks, desired_bondings):
        try:
            configurator.setup(desired_networks, desired_bondings, self._ping)
        except:
            logging.error('Setup failed.', exc_info=True)
            self._cluster.put_attachment_state(
                attachment, 'Failed', 'SetupFailed', traceback.format_exc())
        else:
            self._cluster.put_attachment_state(
                attachment, 'Success', save_spec_to_state=True)

    def _ping(self):
        try:
            self._cluster.get_root()
            logging.debug('Successfully pinged API server.')
            return True
        except:
            logging.debug('Failed to ping API server.')
            return False

    def _merge(self, attachment, attachment_body, networks, bondings):
        logging.debug('Merging %s %s %s', attachment_body, networks, bondings)

        networks_by_names = {
            network['metadata']['name']: network for network in networks
            if 'Success' in network['state']['status']}
        bondings_by_names = {
            bonding['metadata']['name']: bonding for bonding in bondings
            if 'Success' in bonding['state']['status']}

        attachment_networks = frozenset(attachment_body.get('networks', []))
        attachment_bondings = frozenset(attachment_body.get('bondings', []))
        attachment_labels = attachment_body.get('labels', {})

        try:
            config_networks = {}
            for network in attachment_networks:
                attrs = copy.deepcopy(networks_by_names[network]['state'])
                attrs.pop('status', None)
                _replace_labels(attrs, attachment_labels)
                config_networks[network] = attrs
            config_bondings = {}
            for bonding in attachment_bondings:
                attrs = copy.deepcopy(bondings_by_names[bonding]['state'])
                attrs.pop('status', None)
                _replace_labels(attrs, attachment_labels)
                config_bondings[bonding] = attrs
        except:
            logging.warning('Merging failed.', exc_info=True)
            self._cluster.put_attachment_state(
                attachment, 'Failed', 'MergingFailed', traceback.format_exc())
            raise

        return config_networks, config_bondings


def _replace_labels(attrs, labels):
    logging.debug('Replacing labels %s in %s.', labels, attrs)
    for name, value in six.iteritems(attrs):
        if isinstance(value, _basestring) and value.startswith('$'):
            attrs[name] = labels[value[1:]]
        elif isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, _basestring) and item.startswith('$'):
                    new_list.append(labels[item[1:]])
                else:
                    new_list.append(item)
            attrs[name] = new_list
    logging.debug('Replaced labels, result: %s', attrs)


def _get_token():
    with open(_TOKEN_FILE) as token_file:
        return token_file.read()


def main():
    logging.info('Starting vdsm-net-handler.')
    handler = Handler()
    while True:
        try:
            logging.info('Setting up current configuration.')
            handler.setup()
        except:
            logging.exception('Setup failed.')
        time.sleep(8 + random.randrange(8))
