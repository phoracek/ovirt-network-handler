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

import logging
import os
import time
import traceback

from . import configurator, cluster

_TOKEN_FILE = '/var/run/secrets/kubernetes.io/serviceaccount/token'


class Handler(object):

    def __init__(self):
        logging.info('Initializing handler.')
        self._node_name = os.environ['HOSTNAME']
        self._cluster = cluster.Cluster(
            'https://{}:{}'.format(os.environ['KUBERNETES_SERVICE_HOST'],
                                   os.environ['KUBERNETES_PORT_443_TCP_PORT']),
            _get_token())
        configurator.init()
        self._configured = -1

    def _setup(self, attachment):
        if attachment['metadata']['resourceVersion'] <= self._configured:
            return

        try:
            configurator.setup(attachment['spec']['networks'],
                               attachment['spec']['bondings'],
                               self._ping)
        except:
            logging.error('Setup failed.', exc_info=True)
            self._configured = self._cluster.put_attachment_state(
                attachment, 'Failed', 'SetupFailed', traceback.format_exc())
        else:
            self._configured = self._cluster.put_attachment_state(
                attachment, 'Success', save_spec_to_state=True)

    def _remove(self, attachment):
        try:
            configurator.setup({}, {}, self._ping)
        except:
            logging.error('Removal failed.', exc_info=True)
            self._configured = self._cluster.post_attachment(attachment)
            self._configured = self._cluster.put_attachment_state(
                attachment, 'Failed', 'RemovalFailed', traceback.format_exc())

    def _ping(self):
        try:
            self._cluster.get_root()
            logging.debug('Successfully pinged API server.')
            return True
        except:
            logging.debug('Failed to ping API server.')
            return False

    def run(self):
        if self._cluster.get_attachment(self._node_name) is None:
            configurator.setup({}, {}, self._ping)
        for event in self._cluster.watch_attachment(self._node_name):
            if event['type'] in ('ADDED', 'MODIFIED'):
                self._setup(event['object'])
            elif event['type'] == 'DELETED':
                self._remove(event['object'])
            elif event['type'] == 'ERROR':
                logging.warning('Caught an ERROR event: %s', event)


def _get_token():
    with open(_TOKEN_FILE) as token_file:
        return token_file.read()


def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info('Starting vdsm-net-handler.')
    handler = Handler()
    while True:
        try:
            handler.run()
        except:
            logging.exception('Handler failed, restarting.')
        time.sleep(8)
