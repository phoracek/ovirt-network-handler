# oVirt Network Handler

[![Build Status](https://travis-ci.org/phoracek/ovirt-network-handler.svg?branch=master)](https://travis-ci.org/phoracek/ovirt-network-handler)

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
pod. **TODO** limit cluster administration to OvirtNetwork* objects.

```shell
oc create serviceaccount privilegeduser
oc adm policy add-scc-to-user privileged -z privilegeduser
oc policy add-role-to-user cluster-admin system:serviceaccount:ovirt:privilegeduser
```

Install network handler.

```shell
oc apply -f https://raw.githubusercontent.com/phoracek/ovirt-network-handler/master/manifests/add-on.yml
```


### Get capabilities and statistics

Read capabilities and statistics from all nodes.

```shell
oc get ovirtnetworkinfos -o yaml
```

```yaml
apiVersion: v1
items:
- apiVersion: ovirt.org/v1alpha1
  kind: OvirtNetworkInfo
  metadata:
    creationTimestamp: 2017-08-10T12:37:44Z
    name: minishift
    namespace: ovirt
    resourceVersion: "1598"
    selfLink: /apis/ovirt.org/v1alpha1/namespaces/ovirt/ovirtnetworkinfos/minishift
    uid: b4fa636c-7dc8-11e7-a199-525400ee8827
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
            bridge_id: 8000.0242afe6cd09
            default_pvid: "1"
            forward_delay: "1500"
            gc_timer: "14731"
            group_addr: 1:80:c2:0:0:0
            group_fwd_mask: "0x0"
            hash_elasticity: "4"
            hash_max: "512"
            hello_time: "200"
            hello_timer: "104"
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
            root_id: 8000.0242afe6cd09
            root_path_cost: "0"
            root_port: "0"
            stp_state: "0"
            tcn_timer: "0"
            topology_change: "0"
            topology_change_detected: "0"
            topology_change_timer: "0"
            vlan_filtering: "0"
          ports:
          - vethce915a0
          stp: "off"
      nameservers:
      - 192.168.122.1
      - 192.168.42.1
      networks: {}
      nics:
        eth0:
          addr: 192.168.122.142
          dhcpv4: true
          dhcpv6: false
          gateway: 192.168.122.1
          hwaddr: 52:54:00:ee:88:27
          ipv4addrs:
          - 192.168.122.142/24
          ipv4defaultroute: true
          ipv6addrs: []
          ipv6autoconf: true
          ipv6gateway: '::'
          mtu: "1500"
          netmask: 255.255.255.0
          speed: 100
        eth1:
          addr: 192.168.42.44
          dhcpv4: true
          dhcpv6: false
          gateway: ""
          hwaddr: 52:54:00:0a:e5:09
          ipv4addrs:
          - 192.168.42.44/24
          ipv4defaultroute: false
          ipv6addrs: []
          ipv6autoconf: true
          ipv6gateway: '::'
          mtu: "1500"
          netmask: 255.255.255.0
          speed: 100
      supportsIPv6: true
      vlans: {}
    kernel_config:
      bondings: {}
      networks: {}
    statistics:
      docker0:
        name: docker0
        rx: "709610"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.5023688e+09
        speed: "1000"
        state: up
        tx: "1158350"
        txDropped: "0"
        txErrors: "0"
      eth0:
        name: eth0
        rx: "1117690014"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.5023688e+09
        speed: "100"
        state: up
        tx: "7393157"
        txDropped: "0"
        txErrors: "0"
      eth1:
        name: eth1
        rx: "481220"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.5023688e+09
        speed: "100"
        state: up
        tx: "1203526"
        txDropped: "0"
        txErrors: "0"
      lo:
        name: lo
        rx: "61428419"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.5023688e+09
        speed: "1000"
        state: up
        tx: "61428419"
        txDropped: "0"
        txErrors: "0"
      vethce915a0:
        name: vethce915a0
        rx: "264972"
        rxDropped: "0"
        rxErrors: "0"
        sampleTime: 1.5023688e+09
        speed: "1000"
        state: up
        tx: "245580"
        txDropped: "0"
        txErrors: "0"
    status:
      Success:
        message: ""
        reason: ""
kind: List
metadata: {}
resourceVersion: ""
selfLink: ""
```

### Configure networks

Create a bonding on top of node's default interface and then setup a bridge
on it. **TODO** research why is `oc patch` not working.

```shell
vim network_attachment.yml
```

```yaml
apiVersion: 'ovirt.org/v1alpha1'
kind: OvirtNetworkAttachment
metadata:
  name: minishift
spec:
  networks:
    net1:
      bridged: true
      southbound: bond1
      bootproto: dhcp
      defaultRoute: true
  bondings:
    bond1:
      options: 'mode=4 miimon=100'
      nics:
        - eth1
```


```shell
oc create -f network_attachment.yml
oc get ovirtnetworkattachments -o yaml
```

```yaml
apiVersion: v1
items:
- apiVersion: ovirt.org/v1alpha1
  kind: OvirtNetworkAttachment
  metadata:
    creationTimestamp: 2017-08-10T12:39:47Z
    name: minishift
    namespace: ovirt
    resourceVersion: "1622"
    selfLink: /apis/ovirt.org/v1alpha1/namespaces/ovirt/ovirtnetworkattachments/minishift
    uid: feb6acaf-7dc8-11e7-a199-525400ee8827
  spec:
    bondings:
      bond1:
        nics:
        - eth1
        options: mode=4 miimon=100
    networks:
      net1:
        southbound: bond1
        bootproto: dhcp
        bridged: true
        defaultRoute: true
  state:
    configured:
      bondings:
        bond1:
          nics:
          - eth1
          options: mode=4 miimon=100
      networks:
        net1:
          southbound: bond1
          bootproto: dhcp
          bridged: true
          defaultRoute: true
    status:
      Success:
        message: ""
        reason: ""
kind: List
metadata: {}
resourceVersion: ""
selfLink: ""
```
