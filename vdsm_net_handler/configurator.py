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
import threading
import time

import six

from vdsm.network import api as netapi
from vdsm.network import canonicalize
from vdsm.network.netconfpersistence import BaseConfig, RunningConfig
from vdsm.network.nm import networkmanager

_CLIENT_LOG = '/var/run/vdsm/client.log'
_CONNECTIVITY_TIMEOUT = 60


class SetupError(Exception):
    pass


def init():
    logging.info('Initializing VDSM components.')
    networkmanager.init()


def setup(networks, bondings, ping_fn):
    logging.info('Running VDSM setup of desired config: %s %s',
                 networks, bondings)
    canonicalize.canonicalize_networks(networks)
    canonicalize.canonicalize_bondings(bondings)
    _canonicalize_bondings(bondings)
    desired = BaseConfig(networks, bondings)
    diff = desired.diffFrom(RunningConfig())
    logging.info('Configuration difference to be applied: %s %s',
                 diff.networks, diff.bonds)

    if diff:
        ping_thread = threading.Thread(target=_check_ping,
                                       args=(ping_fn, _CONNECTIVITY_TIMEOUT))
        ping_thread.start()

        netapi.setupNetworks(diff.networks, diff.bonds,
                             {'connectivityCheck': True,
                              'connectivityTimeout': _CONNECTIVITY_TIMEOUT})

    logging.info('Setup is now complete.')


def _check_ping(ping_fn, timeout):
    logging.debug('Ping check started with function %s and timeout %s',
                  ping_fn, timeout)
    time_start = _time()
    while True:
        time_passed = _time() - time_start
        if time_passed > timeout:
            logging.debug('Ping check over, exiting.')
            return

        logging.debug('Running ping function.')
        if ping_fn():
            logging.debug('Successfully pinged, logging.')
            with open(_CLIENT_LOG, 'w') as client_log_file:
                client_log_file.write('I have seen my master.\n')
        time.sleep(1)


def _time():
    return os.times()[4]


# TODO: remove when vdsm bondings canonicalization adds mode
def _canonicalize_bondings(bondings):
    for attrs in six.itervalues(bondings):
        if 'options' not in attrs:
            attrs['options'] = 'mode=0'
        elif 'mode=' not in attrs['options']:
            attrs['options'] += ' mode=0'
