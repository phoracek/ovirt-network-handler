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
from vdsm.network import canonicalize, netswitch
from vdsm.network.netconfpersistence import BaseConfig, RunningConfig
from vdsm.network.netinfo.cache import NetInfo
from vdsm.network.netinfo.nics import operstate
from vdsm.network.nm import networkmanager

_CLIENT_LOG = '/var/run/vdsm/client.log'
_CONNECTIVITY_TIMEOUT = 60


class SetupError(Exception):
    pass


def init():
    logging.info('Initializing VDSM components.')
    networkmanager.init()


def setup(ovirt_networks, ovirt_bondings, ping_fn):
    networks, bondings = _ovirt2vdsm(ovirt_networks, ovirt_bondings)
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


def _ovirt2vdsm(networks, bondings):
    vdsm_bondings = {}
    for bonding in bondings:
        attrs = {}
        ovirt_nics = _rget(bonding, ('bonding', 'slaves', 'hostNic'), [])
        attrs['nics'] = [nic['name'] for nic in ovirt_nics]
        ovirt_options = _rget(bonding, ('bonding', 'options', 'option'), [])
        attrs['options'] = ' '.join([
            '{}={}'.format(option['name'], option['value'])
            for option in ovirt_options])
        vdsm_bondings[bonding['name']] = attrs

    vdsm_networks = {}
    for network in networks:
        attrs = {}

        ovirt_mtu = _rget(network, ('network', 'mtu'))
        if ovirt_mtu is not None:
            attrs['mtu'] = int(ovirt_mtu)
        ovirt_stp = _rget(network, ('network', 'stp'))
        if ovirt_stp is not None:
            attrs['stp'] = ovirt_stp.lower() == 'true'
        ovirt_vlan = _rget(network, ('network', 'vlan', 'id'))
        if ovirt_vlan is not None:
            attrs['vlan'] = int(ovirt_vlan)
        ovirt_usages = _rget(network, ('network', 'usages', 'usage'), [])
        attrs['bridged'] = 'vm' in ovirt_usages
        attrs['defaultRoute'] = 'default_route' in ovirt_usages

        ovirt_nic = _rget(network, ('hostNic', 'name'))
        if ovirt_nic:
            if ovirt_nic in vdsm_bondings:
                attrs['bonding'] = ovirt_nic
            else:
                attrs['nic'] = ovirt_nic

        ovirt_ip_assignments = _rget(
            network, ('ipAddressAssignments', 'ipAddressAssignment'), [])
        for assignment in ovirt_ip_assignments:
            if _rget(network, ('ip', 'version'), 'v4') == 'v4':
                method = assignment.get('assignmentMethod', 'none')
                if method == 'dhcp':
                    attrs['bootproto'] = 'dhcp'
                elif method == 'static':
                    attrs['ipaddr'] = assignment['ip']['address']
                    attrs['netmask'] = assignment['ip']['netmask']
                    if 'gateway' in assignment['ip']:
                        attrs['gateway'] = assignment['ip']['gateway']
                break

        ovirt_nameservers = _rget(
            network,
            ('dnsResolverConfiguration', 'nameServers', 'nameServer'), [])
        if ovirt_nameservers:
            attrs['nameserves'] = ovirt_nameservers

        vdsm_networks[network['network']['name']] = attrs

    return vdsm_networks, vdsm_bondings


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
        time.sleep(10)


def _time():
    return os.times()[4]


# TODO: remove when vdsm bondings canonicalization adds mode
def _canonicalize_bondings(bondings):
    for attrs in six.itervalues(bondings):
        if 'options' not in attrs:
            attrs['options'] = 'mode=0'
        elif 'mode=' not in attrs['options']:
            attrs['options'] += ' mode=0'


def get_info(spec):
    network_spec_by_name = {
        network_spec['network']['name']: network_spec
        for network_spec in spec.get('networks', [])}
    info = {'hostNics': [], 'networkAttachments': []}
    netinfo = NetInfo(netswitch.netinfo())

    for name, attrs in six.viewitems(netinfo.networks):
        network = {'name': name}

        ip_address_assignments = (network
                                  .setdefault('ipAddressAssignments', {})
                                  .setdefault('ipAddressAssignment', []))

        ipv4 = {}
        addr = attrs['addr']
        if addr:
            if attrs['dhcpv4']:
                ipv4['assignmentMethod'] = 'dhcp'
                ipv4['ip'] = {'version': 'v4'}
            else:
                ipv4['assignmentMethod'] = 'static'
                ipv4['ip'] = {'address': addr, 'netmask': attrs['netmask']}
                gateway = attrs['gateway']
                if gateway:
                    ipv4['ip']['gateway'] = gateway
        else:
            ipv4['assignmentMethod'] = 'none'
            ipv4['ip'] = {'version': 'v4'}
        ip_address_assignments.append(ipv4)
        # TODO: ipv6

        reported_configurations = (network
                                   .setdefault('reportedConfigurations', {})
                                   .setdefault('reportedConfiguration', []))

        mtu = {'name': 'mtu', 'actualValue': str(attrs['mtu'])}
        bridged = {
            'name': 'bridged', 'actualValue': str(attrs['bridged']).lower()}
        vlan = {'name': 'vlan'}
        if 'vlan' in attrs:
            vlan['actualValue'] = attrs['vlan']
        ipv4_boot_protocol = {
            'name': 'ipv4_boot_protocol',
            'actualValue': 'DHCP' if attrs['dhcpv4'] else 'STATIC'}

        spec_network = network_spec_by_name.get(name)
        if spec_network:
            in_sync = True

            if 'mtu' in spec_network['network']:
                mtu['expectedValue'] = str(spec_network['network']['mtu'])
                mtu_in_sync = mtu['actualValue'] == mtu['expectedValue']
            else:
                mtu_in_sync = True
            mtu['inSync'] = str(mtu_in_sync).lower()
            in_sync &= mtu_in_sync

            ovirt_usages = _rget(
                spec_network, ('network', 'usages', 'usage'), [])
            bridged['expectedValue'] = str('vm' in ovirt_usages).lower()
            bridged_in_sync = (
                bridged['actualValue'] == bridged['expectedValue'])
            bridged['inSync'] = str(bridged_in_sync).lower()
            in_sync &= bridged_in_sync

            ovirt_vlan = _rget(network, ('network', 'vlan', 'id'))
            if ovirt_vlan:
                vlan['expectedValue'] = str(ovirt_vlan)
                vlan_in_sync = vlan['actualValue'] == vlan['expectedValue']
            else:
                vlan_in_sync = True
            vlan['inSync'] = str(vlan_in_sync).lower()
            in_sync &= vlan_in_sync

            ovirt_ip_assignments = _rget(
                spec_network,
                ('ipAddressAssignments', 'ipAddressAssignment'), [])
            method = None
            for assignment in ovirt_ip_assignments:
                if _rget(network, ('ip', 'version'), 'v4') == 'v4':
                    method = assignment.get('assignmentMethod', 'none')
                    break
            if method:
                ipv4_boot_protocol['expectedValue'] = method.upper()
                ipv4_boot_protocol_in_sync = (
                    ipv4_boot_protocol['actualValue'] ==
                    ipv4_boot_protocol['expectedValue'])
            else:
                ipv4_boot_protocol_in_sync = True
            ipv4_boot_protocol['inSync'] = \
                str(ipv4_boot_protocol_in_sync).lower()
            in_sync &= ipv4_boot_protocol_in_sync
        else:
            in_sync = False
        network['inSync'] = str(in_sync).lower()
        reported_configurations.extend([
            mtu, bridged, vlan, ipv4_boot_protocol])
        info['networkAttachments'].append(network)

    for name, spec_network in six.viewitems(network_spec_by_name):
        if name in netinfo.networks:
            continue

        network = {'name': name, 'isSync': 'false'}

        (network
         .setdefault('ipAddressAssignments', {})
         .setdefault('ipAddressAssignment', []))

        reported_configurations = (network
                                   .setdefault('reportedConfigurations', {})
                                   .setdefault('reportedConfiguration', []))

        mtu = {'name': 'mtu'}
        bridged = {'name': 'bridged'}
        vlan = {'name': 'vlan'}
        ipv4_boot_protocol = {'name': 'ipv4_boot_protocol'}

        if 'mtu' in spec_network['network']:
            mtu['expectedValue'] = str(spec_network['network']['mtu'])
        mtu['inSync'] = 'false'

        ovirt_usages = _rget(
            spec_network, ('network', 'usages', 'usage'), [])
        bridged['expectedValue'] = str('vm' in ovirt_usages).lower()
        bridged['inSync'] = 'false'

        ovirt_vlan = _rget(network, ('network', 'vlan', 'id'))
        if ovirt_vlan:
            vlan['expectedValue'] = str(ovirt_vlan)
        vlan['inSync'] = 'false'

        ovirt_ip_assignments = _rget(
            spec_network,
            ('ipAddressAssignments', 'ipAddressAssignment'), [])
        method = None
        for assignment in ovirt_ip_assignments:
            if _rget(network, ('ip', 'version'), 'v4') == 'v4':
                method = assignment.get('assignmentMethod', 'none')
                break
        if method:
            ipv4_boot_protocol['expectedValue'] = method.upper()
        ipv4_boot_protocol['inSync'] = 'false'

        reported_configurations.extend([
            mtu, bridged, vlan, ipv4_boot_protocol])
        info['networkAttachments'].append(network)

    for name, attrs in six.iteritems(netinfo.nics):
        nic = _vdsm_netinfo2ovirt(name, attrs, netinfo)
        info['hostNics'].append(nic)

    for name, attrs in six.iteritems(netinfo.bondings):
        bonding = _vdsm_netinfo2ovirt(name, attrs, netinfo)
        if 'ad_partner_mac' in attrs:
            bonding['hostNic']['adPartnerMac'] = attrs['ad_partner_mac']
        bonding['hostNic']['bonding'] = {}
        bonding['hostNic']['bonding']['slaves'] = [
            {'hostNic': {'name': slave}} for slave in attrs['slaves']]
        bonding['hostNic']['bonding']['options'] = [
            {'option': {'name': opt_name, 'value': opt_value}}
            for opt_name, opt_value in six.viewitems(attrs['opts'])]
        info['hostNics'].append(bonding)

    for name, attrs in six.iteritems(netinfo.vlans):
        vlan = _vdsm_netinfo2ovirt(name, attrs, netinfo)
        vlan['hostNic']['vlan'] = {'id': str(attrs['vlanid'])}
        vlan['hostNic']['baseInterface'] = attrs['iface']
        info['hostNics'].append(vlan)

    return info


def _vdsm_netinfo2ovirt(name, attrs, netinfo):
    # TODO: ipv6
    info = {'hostNic': {
        'name': name,
        'status': operstate(name),
        'mtu': str(attrs['mtu']),
        'bootProtocol': (
            'dhcp' if attrs['dhcpv4'] else
            'static' if attrs['addr'] else
            'none'),
        'bridged': str(bool(netinfo.getBridgedNetworkForIface(name))).lower(),
        'customConfiguration': None,  # TODO
    }}
    if 'hwaddr' in attrs:
        info['hostNic']['mac'] = {'address': attrs['hwaddr']}
    if attrs['addr']:
        addr = {
            'version': 'v4',
            'address': attrs['addr'],
            'netmask': attrs['netmask']}
        if attrs['gateway']:
            addr['gateway'] = attrs['gateway']
        info['hostNic']['ip'] = addr
    return info


def _rget(dictionary, keys, default=None):
    """Recursive dictionary.get()

    >>> rget({'a': {'b': 'hello'}}, ('a', 'b'))
    'hello'
    """
    if dictionary is None:
        return default
    elif len(keys) == 0:
        return dictionary
    return _rget(dictionary.get(keys[0]), keys[1:], default)
