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

from . import _cluster, _system, _vdsm

_PROJECT_NAME = 'ovirt'


class InfoHandler(object):

    def __init__(self):
        logging.info('Initializing handler.')
        self._node_name = os.environ['HOSTNAME']
        self._cluster = _cluster.NodeNetworkInfoCluster(
            self._node_name, _PROJECT_NAME)
        _vdsm.init()
        self._initial_ifaces_sample = _vdsm.InterfacesSample()

    def run(self):
        while True:
            self._refresh_info()
            time.sleep(8)

    def _refresh_info(self):
        logging.info('Refreshing network info.')
        try:
            state = _vdsm.get_info(self._initial_ifaces_sample)
        except:
            logging.error('Info update failed.', exc_info=True)
            state = {'status': {'Failed': {
                'reason': 'GetInfoFailed', 'message': traceback.format_exc()}}}
        else:
            state['status'] = {'Success': {'reason': '', 'message': ''}}
        network_info = {'metadata': {'name': self._node_name}, 'state': state}
        self._cluster.set_network_info(network_info)


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')
    logging.info('Preparing system for vdsm usage.')
    _system.prepare_system()

    logging.info('Starting ovirt-network-info-handler.')

    while True:
        handler = InfoHandler()
        try:
            handler.run()
        except:
            logging.exception('Handler failed, restarting.')
        time.sleep(8)
