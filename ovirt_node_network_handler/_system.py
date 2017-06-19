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

import subprocess


def prepare_system():
    _load_kernel_modules()
    _dump_bonding_options()


def _load_kernel_modules():
    subprocess.check_call(['modprobe', 'bonding'])
    subprocess.check_call(['modprobe', '8021q'])


def _dump_bonding_options():
    subprocess.check_call(['vdsm-tool', 'dump-bonding-options'])
