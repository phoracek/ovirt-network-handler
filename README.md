# oVirt Node Network Handler

oVirt host networking controlled by OpenShift API.


## Demo

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
    creationTimestamp: 2017-05-16T14:58:08Z
    name: minishift
    namespace: ovirt
    resourceVersion: "2157"
    selfLink: /apis/ovirt.org/v1alpha1/namespaces/ovirt/ovirtnodenetworks/minishift
    uid: 12d72c6b-3a48-11e7-8163-5254007f9313
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
            bridge_id: 8000.0242b4241d7c
            default_pvid: "1"
            forward_delay: "1500"
            gc_timer: "20643"
            group_addr: 1:80:c2:0:0:0
            group_fwd_mask: "0x0"
            hash_elasticity: "4"
            hash_max: "512"
            hello_time: "200"
            hello_timer: "99"
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
            root_id: 8000.0242b4241d7c
            root_path_cost: "0"
            root_port: "0"
            stp_state: "0"
            tcn_timer: "0"
            topology_change: "0"
            topology_change_detected: "0"
            topology_change_timer: "0"
            vlan_filtering: "0"
          ports:
          - veth41ed4e0
          stp: "off"
      nameservers:
      - 192.168.122.1
      - 192.168.42.1
      networks: {}
      nics:
        eth0:
          addr: 192.168.122.151
          dhcpv4: true
          dhcpv6: false
          gateway: 192.168.122.1
          hwaddr: 52:54:00:7f:93:13
          ipv4addrs:
          - 192.168.122.151/24
          ipv4defaultroute: true
          ipv6addrs: []
          ipv6autoconf: true
          ipv6gateway: '::'
          mtu: "1500"
          netmask: 255.255.255.0
          speed: 100
        eth1:
          addr: 192.168.42.105
          dhcpv4: true
          dhcpv6: false
          gateway: ""
          hwaddr: 52:54:00:f7:40:1e
          ipv4addrs:
          - 192.168.42.105/24
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
    setupStatus:
      Success:
        message: ""
        reason: ""
    statistics:
      docker0:
        name: docker0
        rx: "831202"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4949468e+09
        speed: "1000"
        state: up
        tx: "1292868"
        txDropped: "0"
        txErrors: "0"
      eth0:
        name: eth0
        rx: "695557910"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4949468e+09
        speed: "100"
        state: up
        tx: "3414634"
        txDropped: "0"
        txErrors: "0"
      eth1:
        name: eth1
        rx: "958014"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4949468e+09
        speed: "100"
        state: up
        tx: "2682596"
        txDropped: "0"
        txErrors: "0"
      lo:
        name: lo
        rx: "81471386"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4949468e+09
        speed: "1000"
        state: up
        tx: "81471386"
        txDropped: "0"
        txErrors: "0"
      veth41ed4e0:
        name: veth41ed4e0
        rx: "409668"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4949468e+09
        speed: "1000"
        state: up
        tx: "380794"
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
    creationTimestamp: 2017-05-17T09:05:36Z
    name: minishift
    namespace: ovirt
    resourceVersion: "1180"
    selfLink: /apis/ovirt.org/v1alpha1/namespaces/ovirt/ovirtnodenetworks/minishift
    uid: fd7db999-3adf-11e7-8b43-5254008b6773
  spec:
    bondings:
      bond1:
        nics:
        - eth1
        options: mode=1 miimon=100
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
          active_slave: eth1
          addr: ""
          dhcpv4: false
          dhcpv6: false
          gateway: ""
          hwaddr: 52:54:00:0c:e6:b1
          ipv4addrs: []
          ipv4defaultroute: false
          ipv6addrs: []
          ipv6autoconf: false
          ipv6gateway: '::'
          mtu: "1500"
          netmask: ""
          opts:
            miimon: "100"
            mode: "1"
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
            bridge_id: 8000.024242411f6c
            default_pvid: "1"
            forward_delay: "1500"
            gc_timer: "16923"
            group_addr: 1:80:c2:0:0:0
            group_fwd_mask: "0x0"
            hash_elasticity: "4"
            hash_max: "512"
            hello_time: "200"
            hello_timer: "20"
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
            root_id: 8000.024242411f6c
            root_path_cost: "0"
            root_port: "0"
            stp_state: "0"
            tcn_timer: "0"
            topology_change: "0"
            topology_change_detected: "0"
            topology_change_timer: "0"
            vlan_filtering: "0"
          ports:
          - veth96a2144
          stp: "off"
        net1:
          addr: 192.168.42.75
          dhcpv4: true
          dhcpv6: false
          gateway: ""
          ipv4addrs:
          - 192.168.42.75/24
          ipv4defaultroute: false
          ipv6addrs: []
          ipv6autoconf: false
          ipv6gateway: '::'
          mtu: "1500"
          netmask: 255.255.255.0
          opts:
            ageing_time: "30000"
            bridge_id: 8000.5254000ce6b1
            default_pvid: "1"
            forward_delay: "0"
            gc_timer: "27162"
            group_addr: 1:80:c2:0:0:0
            group_fwd_mask: "0x0"
            hash_elasticity: "4"
            hash_max: "512"
            hello_time: "200"
            hello_timer: "119"
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
            root_id: 8000.5254000ce6b1
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
        virbr0:
          addr: 192.168.124.1
          dhcpv4: false
          dhcpv6: false
          gateway: ""
          ipv4addrs:
          - 192.168.124.1/24
          ipv4defaultroute: false
          ipv6addrs: []
          ipv6autoconf: false
          ipv6gateway: '::'
          mtu: "1500"
          netmask: 255.255.255.0
          opts:
            ageing_time: "30000"
            bridge_id: 8000.5254002113ac
            default_pvid: "1"
            forward_delay: "200"
            gc_timer: "8321"
            group_addr: 1:80:c2:0:0:0
            group_fwd_mask: "0x0"
            hash_elasticity: "4"
            hash_max: "512"
            hello_time: "200"
            hello_timer: "19"
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
            root_id: 8000.5254002113ac
            root_path_cost: "0"
            root_port: "0"
            stp_state: "1"
            tcn_timer: "0"
            topology_change: "0"
            topology_change_detected: "0"
            topology_change_timer: "0"
            vlan_filtering: "0"
          ports:
          - virbr0-nic
          stp: "on"
      nameservers:
      - 192.168.122.1
      - 192.168.42.1
      networks:
        net1:
          addr: 192.168.42.75
          bridged: true
          dhcpv4: true
          dhcpv6: false
          gateway: ""
          iface: net1
          ipv4addrs:
          - 192.168.42.75/24
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
          addr: 192.168.122.125
          dhcpv4: true
          dhcpv6: false
          gateway: 192.168.122.1
          hwaddr: 52:54:00:8b:67:73
          ipv4addrs:
          - 192.168.122.125/24
          ipv4defaultroute: true
          ipv6addrs: []
          ipv6autoconf: true
          ipv6gateway: '::'
          mtu: "1500"
          netmask: 255.255.255.0
          speed: 100
        eth1:
          addr: ""
          dhcpv4: false
          dhcpv6: false
          gateway: ""
          hwaddr: 52:54:00:0c:e6:b1
          ipv4addrs: []
          ipv4defaultroute: false
          ipv6addrs: []
          ipv6autoconf: false
          ipv6gateway: '::'
          mtu: "1500"
          netmask: ""
          permhwaddr: 52:54:00:0c:e6:b1
          speed: 100
      supportsIPv6: true
      vlans: {}
    infoStatus:
      Success:
        message: ""
        reason: ""
    setupStatus:
      Success:
        message: ""
        reason: ""
    statistics:
      docker0:
        name: docker0
        rx: "526684"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4950124e+09
        speed: "1000"
        state: up
        tx: "970817"
        txDropped: "0"
        txErrors: "0"
      eth0:
        name: eth0
        rx: "695630235"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4950124e+09
        speed: "100"
        state: up
        tx: "3481879"
        txDropped: "0"
        txErrors: "0"
      eth1:
        name: eth1
        rx: "574357"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4950124e+09
        speed: "100"
        state: up
        tx: "1831419"
        txDropped: "0"
        txErrors: "0"
      lo:
        name: lo
        rx: "48252319"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4950124e+09
        speed: "1000"
        state: up
        tx: "48252319"
        txDropped: "0"
        txErrors: "0"
      veth96a2144:
        name: veth96a2144
        rx: "54558"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4950124e+09
        speed: "1000"
        state: up
        tx: "51532"
        txDropped: "0"
        txErrors: "0"
      virbr0:
        name: virbr0
        rx: "0"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4950124e+09
        speed: "1000"
        state: down
        tx: "0"
        txDropped: "0"
        txErrors: "0"
      virbr0-nic:
        name: virbr0-nic
        rx: "0"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.4950124e+09
        speed: "1000"
        state: down
        tx: "0"
        txDropped: "0"
        txErrors: "0"
kind: List
metadata: {}
resourceVersion: ""
selfLink: ""
```
