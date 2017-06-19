# oVirt Node Network Handler

[![Build Status](https://travis-ci.org/phoracek/ovirt-node-network-handler.svg?branch=master)](https://travis-ci.org/phoracek/ovirt-node-network-handler)

oVirt host networking controlled by OpenShift API.


## OpenShift Demo

With following steps you can install test environment with OpenShift cluster,
install network handler there and use to to configure and gather info about
networks.


### Pre-requisites

Must use oc tool version 1.5.0 – https://github.com/openshift/origin/releases


### Running OpenShift environment via Minishift

Minishift is a VM running openshift cluster in it. This mostly being used for
testing for easy and quicker deployment without changing local environment.

Install Minishift – https://docs.openshift.org/latest/minishift/getting-started/installing.html

When using KVM, install docker-machine-driver-kvm – https://docs.openshift.org/latest/minishift/getting-started/docker-machine-drivers.html

Install and start Minishift (single node) cluster running on CentOS 7.

```shell
export OCTAG=v1.5.0
export LATEST_MINISHIFT_CENTOS_ISO_BASE=$(curl -I https://github.com/minishift/minishift-centos-iso/releases/latest | grep "Location" | cut -d: -f2- | tr -d '\r' | xargs)
export MINISHIFT_CENTOS_ISO=${LATEST_MINISHIFT_CENTOS_ISO_BASE/tag/download}/minishift-centos7.iso
minishift start --memory 4096 --cpus 2 --iso-url=$MINISHIFT_CENTOS_ISO --openshift-version=$OCTAG
export PATH=$PATH:~/.minishift/cache/oc/$OCTAG
```


### Install network handler

Loggin to OpenShift as admin.

```shell
oc login -u system:admin
```

Create a new project.

```shell
export PROJECT=ovirt
oc new-project $PROJECT --description="oVirt" --display-name="oVirt"
```

Allows host advanced privileges and cluster administration inside the handler
pod. **TODO** limit cluster administration to OvirtNodeNetwork objects.

```shell
oc create serviceaccount privilegeduser
oc adm policy add-scc-to-user privileged -z privilegeduser
oc policy add-role-to-user cluster-admin system:serviceaccount:ovirt:privilegeduser
```

Install network handler.

```shell
oc apply -f https://raw.githubusercontent.com/phoracek/ovirt-node-network-handler/master/manifests/add-on.yml
```


### Get capabilities and statistics

Read capabilities and statistics from all nodes.

```shell
oc get ovirtnodenetworks -o yaml
```

```yaml
apiVersion: v1
items:
- apiVersion: ovirt.org/v1alpha1
  kind: OvirtNodeNetwork
  metadata:
    creationTimestamp: 2017-06-16T11:07:30Z
    name: minishift
    namespace: ovirt
    resourceVersion: "1151"
    selfLink: /apis/ovirt.org/v1alpha1/namespaces/ovirt/ovirtnodenetworks/minishift
    uid: fd9a490b-5283-11e7-98d1-525400e42a82
  spec: {}
  state:
    capabilities:
      bondings: {}
      bridges:
        docker0:
          addr: 172.17.0.1
          dhcpv4: false
          dhcpv6: false
          gateway: ""
          ipv4addrs:
          - 172.17.0.1/16
          ipv4defaultroute: false
          ipv6addrs: []
          ipv6autoconf: true
          ipv6gateway: '::'
          mtu: "1500"
          netmask: 255.255.0.0
          opts:
            ageing_time: "30000"
            bridge_id: 8000.0242a8153d32
            default_pvid: "1"
            forward_delay: "1500"
            gc_timer: "9393"
            group_addr: 1:80:c2:0:0:0
            group_fwd_mask: "0x0"
            hash_elasticity: "4"
            hash_max: "512"
            hello_time: "200"
            hello_timer: "90"
            max_age: "2000"
            multicast_last_member_count: "2"
            multicast_last_member_interval: "100"
            multicast_membership_interval: "26000"
            multicast_querier: "0"
            multicast_querier_interval: "25500"
            multicast_query_interval: "12500"
            multicast_query_response_interval: "1000"
            multicast_router: "1"
            multicast_snooping: "1"
            multicast_startup_query_count: "2"
            multicast_startup_query_interval: "3125"
            nf_call_arptables: "0"
            nf_call_ip6tables: "0"
            nf_call_iptables: "0"
            priority: "32768"
            root_id: 8000.0242a8153d32
            root_path_cost: "0"
            root_port: "0"
            stp_state: "0"
            tcn_timer: "0"
            topology_change: "0"
            topology_change_detected: "0"
            topology_change_timer: "0"
            vlan_filtering: "0"
          ports:
          - veth5250a08
          stp: "off"
      nameservers:
      - 192.168.122.1
      - 192.168.42.1
      networks: {}
      nics:
        eth0:
          addr: 192.168.122.81
          dhcpv4: true
          dhcpv6: false
          gateway: 192.168.122.1
          hwaddr: 52:54:00:e4:2a:82
          ipv4addrs:
          - 192.168.122.81/24
          ipv4defaultroute: true
          ipv6addrs: []
          ipv6autoconf: true
          ipv6gateway: '::'
          mtu: "1500"
          netmask: 255.255.255.0
          speed: 100
        eth1:
          addr: 192.168.42.212
          dhcpv4: true
          dhcpv6: false
          gateway: ""
          hwaddr: 52:54:00:2d:2b:d7
          ipv4addrs:
          - 192.168.42.212/24
          ipv4defaultroute: false
          ipv6addrs: []
          ipv6autoconf: true
          ipv6gateway: '::'
          mtu: "1500"
          netmask: 255.255.255.0
          speed: 100
      supportsIPv6: true
      vlans: {}
    infoStatus:
      Success:
        message: ""
        reason: ""
    kernel_config:
      bondings: {}
      networks: {}
    setupStatus:
      Success:
        message: ""
        reason: ""
    statistics:
      docker0:
        name: docker0
        rx: "541601"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4976113e+09
        speed: "1000"
        state: up
        tx: "984412"
        txDropped: "0"
        txErrors: "0"
      eth0:
        name: eth0
        rx: "710267176"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4976113e+09
        speed: "100"
        state: up
        tx: "2754155"
        txDropped: "0"
        txErrors: "0"
      eth1:
        name: eth1
        rx: "418556"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4976113e+09
        speed: "100"
        state: up
        tx: "1195523"
        txDropped: "0"
        txErrors: "0"
      lo:
        name: lo
        rx: "44748126"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4976113e+09
        speed: "1000"
        state: up
        tx: "44748126"
        txDropped: "0"
        txErrors: "0"
      veth5250a08:
        name: veth5250a08
        rx: "63522"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4976113e+09
        speed: "1000"
        state: up
        tx: "59386"
        txDropped: "0"
        txErrors: "0"
kind: List
metadata: {}
resourceVersion: ""
selfLink: ""
```

### Add a network

Create a bonding on top of node's default interface and then setup a bridge
on it. **TODO** research why is `oc patch` not working.

```shell
vim node_network.yml
```

```yaml
apiVersion: 'ovirt.org/v1alpha1'
kind: OvirtNodeNetwork
metadata:
  name: minishift
spec:
  networks:
    net1:
      bridged: true
      bonding: bond1
      bootproto: dhcp
      defaultRoute: true
  bondings:
    bond1:
      options: 'mode=4 miimon=100'
      nics:
        - eth1
```


```shell
oc replace ovirtnodenetwork minishift -f node_network.yml
oc get ovirtnodenetworks -o yaml
```

```yaml
apiVersion: v1
items:
- apiVersion: ovirt.org/v1alpha1
  kind: OvirtNodeNetwork
  metadata:
    creationTimestamp: 2017-06-16T11:07:30Z
    name: minishift
    namespace: ovirt
    resourceVersion: "1214"
    selfLink: /apis/ovirt.org/v1alpha1/namespaces/ovirt/ovirtnodenetworks/minishift
    uid: fd9a490b-5283-11e7-98d1-525400e42a82
  spec:
    bondings:
      bond1:
        nics:
        - eth1
        options: mode=4 miimon=100
    networks:
      net1:
        bonding: bond1
        bootproto: dhcp
        bridged: true
        defaultRoute: true
  state:
    capabilities:
      bondings:
        bond1:
          active_slave: ""
          ad_aggregator_id: "2"
          ad_partner_mac: "00:00:00:00:00:00"
          addr: ""
          dhcpv4: false
          dhcpv6: false
          gateway: ""
          hwaddr: 52:54:00:2d:2b:d7
          ipv4addrs: []
          ipv4defaultroute: false
          ipv6addrs: []
          ipv6autoconf: false
          ipv6gateway: '::'
          mtu: "1500"
          netmask: ""
          opts:
            miimon: "100"
            mode: "4"
          slaves:
          - eth1
          switch: legacy
      bridges:
        docker0:
          addr: 172.17.0.1
          dhcpv4: false
          dhcpv6: false
          gateway: ""
          ipv4addrs:
          - 172.17.0.1/16
          ipv4defaultroute: false
          ipv6addrs: []
          ipv6autoconf: true
          ipv6gateway: '::'
          mtu: "1500"
          netmask: 255.255.0.0
          opts:
            ageing_time: "30000"
            bridge_id: 8000.0242a8153d32
            default_pvid: "1"
            forward_delay: "1500"
            gc_timer: "18437"
            group_addr: 1:80:c2:0:0:0
            group_fwd_mask: "0x0"
            hash_elasticity: "4"
            hash_max: "512"
            hello_time: "200"
            hello_timer: "33"
            max_age: "2000"
            multicast_last_member_count: "2"
            multicast_last_member_interval: "100"
            multicast_membership_interval: "26000"
            multicast_querier: "0"
            multicast_querier_interval: "25500"
            multicast_query_interval: "12500"
            multicast_query_response_interval: "1000"
            multicast_router: "1"
            multicast_snooping: "1"
            multicast_startup_query_count: "2"
            multicast_startup_query_interval: "3125"
            nf_call_arptables: "0"
            nf_call_ip6tables: "0"
            nf_call_iptables: "0"
            priority: "32768"
            root_id: 8000.0242a8153d32
            root_path_cost: "0"
            root_port: "0"
            stp_state: "0"
            tcn_timer: "0"
            topology_change: "0"
            topology_change_detected: "0"
            topology_change_timer: "0"
            vlan_filtering: "0"
          ports:
          - veth5250a08
          stp: "off"
        net1:
          addr: 192.168.42.212
          dhcpv4: true
          dhcpv6: false
          gateway: ""
          ipv4addrs:
          - 192.168.42.212/24
          ipv4defaultroute: false
          ipv6addrs: []
          ipv6autoconf: false
          ipv6gateway: '::'
          mtu: "1500"
          netmask: 255.255.255.0
          opts:
            ageing_time: "30000"
            bridge_id: 8000.5254002d2bd7
            default_pvid: "1"
            forward_delay: "0"
            gc_timer: "29189"
            group_addr: 1:80:c2:0:0:0
            group_fwd_mask: "0x0"
            hash_elasticity: "4"
            hash_max: "512"
            hello_time: "200"
            hello_timer: "133"
            max_age: "2000"
            multicast_last_member_count: "2"
            multicast_last_member_interval: "100"
            multicast_membership_interval: "26000"
            multicast_querier: "0"
            multicast_querier_interval: "25500"
            multicast_query_interval: "12500"
            multicast_query_response_interval: "1000"
            multicast_router: "1"
            multicast_snooping: "1"
            multicast_startup_query_count: "2"
            multicast_startup_query_interval: "3125"
            nf_call_arptables: "0"
            nf_call_ip6tables: "0"
            nf_call_iptables: "0"
            priority: "32768"
            root_id: 8000.5254002d2bd7
            root_path_cost: "0"
            root_port: "0"
            stp_state: "0"
            tcn_timer: "0"
            topology_change: "0"
            topology_change_detected: "0"
            topology_change_timer: "0"
            vlan_filtering: "0"
          ports:
          - bond1
          stp: "off"
      nameservers:
      - 192.168.122.1
      - 192.168.42.1
      networks:
        net1:
          addr: 192.168.42.212
          bridged: true
          dhcpv4: true
          dhcpv6: false
          gateway: ""
          iface: net1
          ipv4addrs:
          - 192.168.42.212/24
          ipv4defaultroute: false
          ipv6addrs: []
          ipv6autoconf: false
          ipv6gateway: '::'
          mtu: "1500"
          netmask: 255.255.255.0
          ports:
          - bond1
          stp: "off"
          switch: legacy
      nics:
        eth0:
          addr: 192.168.122.81
          dhcpv4: true
          dhcpv6: false
          gateway: 192.168.122.1
          hwaddr: 52:54:00:e4:2a:82
          ipv4addrs:
          - 192.168.122.81/24
          ipv4defaultroute: true
          ipv6addrs: []
          ipv6autoconf: true
          ipv6gateway: '::'
          mtu: "1500"
          netmask: 255.255.255.0
          speed: 100
        eth1:
          ad_aggregator_id: "2"
          addr: ""
          dhcpv4: false
          dhcpv6: false
          gateway: ""
          hwaddr: 52:54:00:2d:2b:d7
          ipv4addrs: []
          ipv4defaultroute: false
          ipv6addrs: []
          ipv6autoconf: false
          ipv6gateway: '::'
          mtu: "1500"
          netmask: ""
          permhwaddr: 52:54:00:2d:2b:d7
          speed: 100
      supportsIPv6: true
      vlans: {}
    infoStatus:
      Success:
        message: ""
        reason: ""
    kernel_config:
      bondings:
        bond1:
          nics:
          - eth1
          options: miimon=100 mode=4
          switch: legacy
      networks:
        net1:
          bonding: bond1
          bootproto: dhcp
          bridged: true
          defaultRoute: false
          dhcpv6: false
          ipv6autoconf: false
          mtu: 1500
          nameservers: []
          stp: false
          switch: legacy
    setupStatus:
      Success:
        message: ""
        reason: ""
    statistics:
      docker0:
        name: docker0
        rx: "559577"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4976115e+09
        speed: "1000"
        state: up
        tx: "1003732"
        txDropped: "0"
        txErrors: "0"
      eth0:
        name: eth0
        rx: "710268436"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4976115e+09
        speed: "100"
        state: up
        tx: "2755631"
        txDropped: "0"
        txErrors: "0"
      eth1:
        name: eth1
        rx: "444984"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4976115e+09
        speed: "100"
        state: up
        tx: "1263107"
        txDropped: "0"
        txErrors: "0"
      lo:
        name: lo
        rx: "47797763"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4976115e+09
        speed: "1000"
        state: up
        tx: "47797763"
        txDropped: "0"
        txErrors: "0"
      veth5250a08:
        name: veth5250a08
        rx: "84438"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4976115e+09
        speed: "1000"
        state: up
        tx: "78706"
        txDropped: "0"
        txErrors: "0"
kind: List
metadata: {}
resourceVersion: ""
selfLink: ""
```
