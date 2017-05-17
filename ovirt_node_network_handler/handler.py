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
import threading
import time
import traceback

from . import _cluster, _vdsm

try:
    import Queue as queue
except ImportError:  # Python 3
    import queue

_PROJECT_NAME = 'ovirt'


class Handler(object):

    def __init__(self):
        logging.info('Initializing handler.')
        self._node_name = os.environ['HOSTNAME']
        self._cluster = _cluster.NodeNetworkCluster(
            self._node_name, _PROJECT_NAME)
        _vdsm.init()
        self._initial_ifaces_sample = _vdsm.InterfacesSample()
        self._configured = -1

    def run(self):
        if self._cluster.get_network() is None:
            _vdsm.setup({}, {}, self._ping)
            self._refresh({'metadata': {'name': self._node_name}})
        for event in self._monitor():
            if event is None:
                network = self._cluster.get_network()
                self._refresh(network)
            elif event['type'] in ('ADDED', 'MODIFIED'):
                self._setup(event['object'])
            elif event['type'] == 'DELETED':
                self._remove(event['object'])
            elif event['type'] == 'ERROR':
                logging.error('Caught an ERROR event: %s', event)

    def _monitor(self):
        events = queue.Queue()

        def network_monitor():
            for event in self._cluster.watch_network():
                events.put(event)

        thread = threading.Thread(target=network_monitor)
        thread.daemon = True
        thread.start()

        while True:
            try:
                yield events.get(timeout=10)
            except queue.Empty:
                yield None

    def _setup(self, network):
        if int(network['metadata']['resourceVersion']) <= self._configured:
            return

        logging.info('Setting up network.')
        try:
            spec = network.setdefault('spec', {})
            ovirt_networks = copy.deepcopy(spec.get('networks', {}))
            ovirt_bondings = copy.deepcopy(spec.get('bondings', {}))
            logging.info('Running setup of desired oVirt config: %s %s',
                         ovirt_networks, ovirt_bondings)
            _vdsm.setup(ovirt_networks, ovirt_bondings, self._ping)
        except:
            logging.error('Setup failed.', exc_info=True)
            network.setdefault('state', {})['setupStatus'] = {'Failed': {
                'reason': 'SetupFailed', 'message': traceback.format_exc()}}
        else:
            network.setdefault('state', {})['setupStatus'] = {'Success': {
                'reason': '', 'message': ''}}

        self._update_info(network)

        self._configured = self._cluster.set_network(network)

    def _remove(self, network):
        logging.info('Removing network.')
        try:
            _vdsm.setup({}, {}, self._ping)
            network['spec'] = {}
        except:
            logging.error('Removal failed.', exc_info=True)
            network.setdefault('state', {})['setupStatus'] = {'Failed': {
                'reason': 'RemovalFailed', 'message': traceback.format_exc()}}
        else:
            network.setdefault('state', {})['setupStatus'] = {'Success': {
                'reason': '', 'message': ''}}

        self._update_info(network)

        self._configured = self._cluster.set_network(network)

    def _refresh(self, network):
        logging.info('Refreshing network info.')
        self._update_info(network)
        self._configured = self._cluster.set_network(network)

    def _update_info(self, network):
        network.setdefault('spec', {})

        try:
            info = _vdsm.get_info(self._initial_ifaces_sample)
        except:
            logging.error('Info update failed.', exc_info=True)
            info = {'infoStatus': {'Failed': {
                'reason': 'GetInfoFailed', 'message': traceback.format_exc()}}}
        else:
            info['infoStatus'] = {'Success': {'reason': '', 'message': ''}}

        network.setdefault(
            'state',
            {'setupStatus': {'Success': {'reason': '', 'message': ''}}}
        ).update(info)

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
    logging.info('Starting vdsm-net-handler.')

    while True:
        handler = Handler()
        try:
            handler.run()
        except:
            logging.exception('Handler failed, restarting.')
        time.sleep(8)
