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
import time
import traceback

from . import _cluster, _system, _vdsm

_PROJECT_NAME = 'ovirt'


class AttachmentHandler(object):

    def __init__(self):
        logging.info('Initializing handler.')
        self._node_name = os.environ['HOSTNAME']
        self._cluster = _cluster.NodeNetworkAttachmentCluster(
            self._node_name, _PROJECT_NAME)
        _vdsm.init()
        self._configured = -1

    def run(self):
        if self._cluster.get_network_attachment() is None:
            _vdsm.setup({}, {}, self._ping)
        for event in self._cluster.watch_network_attachment():
            if event['type'] in ('ADDED', 'MODIFIED'):
                self._setup(event['object'])
            elif event['type'] == 'DELETED':
                self._remove(event['object'])
            elif event['type'] == 'ERROR':
                logging.error('Caught an ERROR event: %s', event)

    def _setup(self, attachment):
        if int(attachment['metadata']['resourceVersion']) <= self._configured:
            return

        logging.info('Setting up network attachment.')
        try:
            spec = attachment.setdefault('spec', {})
            ovirt_networks = copy.deepcopy(spec.get('networks', {}))
            ovirt_bondings = copy.deepcopy(spec.get('bondings', {}))
            logging.info('Running setup of desired oVirt config: %s %s',
                         ovirt_networks, ovirt_bondings)
            _vdsm.setup(ovirt_networks, ovirt_bondings, self._ping)
        except:
            logging.error('Setup failed.', exc_info=True)
            attachment.setdefault('state', {})['status'] = {'Failed': {
                'reason': 'SetupFailed', 'message': traceback.format_exc()}}
        else:
            attachment['state'] = {
                'status': {
                    'Success': {'reason': '', 'message': ''}
                },
                'configured': spec  # XXX: no need for copy?
            }

        self._configured = self._cluster.set_network_attachment(attachment)

    def _remove(self, attachment):
        logging.info('Removing network attachment.')
        try:
            _vdsm.setup({}, {}, self._ping)
            attachment['spec'] = {}
        except:
            logging.error('Removal failed.', exc_info=True)
            attachment.setdefault('state', {})['status'] = {'Failed': {
                'reason': 'RemovalFailed', 'message': traceback.format_exc()}}
        else:
            attachment['state'] = {
                'status': {
                    'Success': {'reason': '', 'message': ''}
                },
                'configured': {}
            }

        self._configured = self._cluster.set_network_attachment(attachment)

    def _ping(self):
        try:
            self._cluster.get('')
            logging.debug('Successfully pinged API server.')
            return True
        except:
            logging.debug('Failed to ping API server.')
            return False


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')
    logging.info('Preparing system for vdsm usage.')
    _system.prepare_system()

    logging.info('Starting ovirt-node-network-attachment-handler.')

    while True:
        handler = AttachmentHandler()
        try:
            handler.run()
        except:
            logging.exception('Handler failed, restarting.')
        time.sleep(8)
