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

from __future__ import print_function

import json
import select
import sys

import yaml

from . import _system, _vdsm

TIMEOUT = 60


def setup_networks():
    _init()

    perform_connectivity_check = '-y' not in sys.argv
    post_setup_function = (
        _connectivity_check if perform_connectivity_check
        else _no_connectivity_check
    )

    data = _read_and_parse_stdin()
    networks = data['networks']
    bondings = data['bondings']

    print('[*] Starting networks setup.')
    diff = _vdsm.setup(networks, bondings, post_setup_function)
    # NOTE: we never get here, setup is blocking, waiting for con check
    if not diff:
        print('[*] Desired state is already in place, nothing to do.')


def _connectivity_check():
    print('[*] Setup is done.')
    print('[**] Accept current state with "y" within next 60 second, '
          'otherwise rollback will be started.')

    inp, _, _ = select.select([sys.stdin], [], [], TIMEOUT)
    if inp:
        answer = inp[0].readline().strip()
        if answer == 'y':
            print('[**] Configuration accepted.')
            return True
        else:
            print('[**] Rollback triggered.')
            raise RuntimeError('Network configuration was rejected.')

    print('[**] No user response caught, starting rollback to previous state.')
    raise RuntimeError('Network configuration was not accepted.')


def _no_connectivity_check():
    print('[*] Setup is done, skipping connectivity check.')
    return True


def _read_and_parse_stdin():
    input_lines = sys.stdin.read()
    try:
        return yaml.load(input_lines)
    except:
        return json.loads(input_lines)


def _init():
    _system.prepare_system()
    _vdsm.init()
