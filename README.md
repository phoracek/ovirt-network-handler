# oVirt Host Network Handler

oVirt host networking controlled by OpenShift API.

## Warning

- Don't look at the code...
- Don't check out master branch, I'm force pushing!

## Usage

Make sure `libvirtd` is installed and running on all nodes. You also need to
`modprobe bonding` and `modprobe 8021q` on each node in order to be able to
use kernel modules in containers.

`OvirtHostNetwork` TPR and `DaemonSet` with `ovirt-host-network-handler`
running.

```shell
kubectl apply -f https://raw.githubusercontent.com/phoracek/ovirt-host-network-handler/master/manifests/add-on.yml
```

And finally apply network configuration.

```shell
kubectl replace -f ...
```

```yaml
---
apiVersion: 'ovirt.org/v1alpha1'
kind: OvirtHostNetwork
metadata:
  name: node1
spec:
  networks:
    - network:
        name: net1
        mtu: '1500'
        stp: 'true'
        usages:
          usage:
            - vm
      hostNic:
        name: bond1
      ipAddressAssignments:
        ipAddressAssignment:
          - assignmentMethod: dhcp
            ip:
              version: v4
      dnsResolverConfiguration:
        nameServers:
          nameServer:
            - '1.1.1.1'
            - '2.2.2.2'
  bondings:
    - name: bond1
      bonding:
        options:
          option:
            - name: mode
              value: '4'
            - name: miimon
              value: '100'
        slaves:
          hostNic:
            - name: eth0
            - name: eth1
```

An example of a report:

```shell
kubectl get ovirthostnetworks -o yaml
```

```yaml
apiVersion: v1
items:
- apiVersion: ovirt.org/v1alpha1
  kind: OvirtHostNetwork
  metadata:
    creationTimestamp: 2017-03-17T13:17:11Z
    name: master
    namespace: default
    resourceVersion: "9690"
    selfLink: /apis/ovirt.org/v1alpha1/namespaces/default/ovirthostnetworks/master
    uid: 07e8120c-0b14-11e7-ab65-525400d59c70
  spec: {}
  state:
    hostNics:
    - hostNic:
        bootProtocol: dhcp
        bridged: "False"
        customConfiguration: null
        ip:
          address: 192.168.121.246
          gateway: 192.168.121.1
          netmask: 255.255.255.0
          version: v4
        mtu: "1500"
        name: eth0
        status: up
      mac:
        address: 52:54:00:d5:9c:70
    - hostNic:
        bootProtocol: none
        bridged: "False"
        customConfiguration: null
        mtu: "1500"
        name: bond0
        options:
        - option:
            name: mode
            value: "0"
        slaves: []
        status: down
      mac:
        address: 9a:56:d7:50:87:72
    infoStatus:
      Success:
        message: ""
        reason: ""
    networkAttachments: []
    setupStatus:
      Success:
        message: ""
        reason: ""
- apiVersion: ovirt.org/v1alpha1
  kind: OvirtHostNetwork
  metadata:
    creationTimestamp: 2017-03-17T13:17:22Z
    name: node1
    namespace: default
    resourceVersion: "9695"
    selfLink: /apis/ovirt.org/v1alpha1/namespaces/default/ovirthostnetworks/node1
    uid: 0e2a4254-0b14-11e7-ab65-525400d59c70
  spec:
    bondings:
    - bonding:
        options:
          option:
          - name: mode
            value: "4"
          - name: miimon
            value: "100"
        slaves:
          hostNic:
          - name: dummy_1
      name: bond1
    networks:
    - hostNic:
        name: bond1
      ipAddressAssignments:
        ipAddressAssignment:
        - assignmentMethod: static
          ip:
            address: 10.10.10.2
            netmask: 255.255.255.0
            version: v4
      network:
        mtu: "1490"
        name: net1
        stp: "true"
        usages:
          usage:
          - vm
        vlan:
          id: 10
  state:
    hostNics:
    - hostNic:
        bootProtocol: none
        bridged: "False"
        customConfiguration: null
        mtu: "1490"
        name: dummy_1
        status: unknown
      mac:
        address: d6:0b:90:af:6c:c5
    - hostNic:
        bootProtocol: dhcp
        bridged: "False"
        customConfiguration: null
        ip:
          address: 192.168.121.51
          gateway: 192.168.121.1
          netmask: 255.255.255.0
          version: v4
        mtu: "1500"
        name: eth0
        status: up
      mac:
        address: 52:54:00:3d:33:20
    - hostNic:
        bootProtocol: none
        bridged: "False"
        customConfiguration: null
        mtu: "1500"
        name: bond0
        options:
        - option:
            name: mode
            value: "0"
        slaves: []
        status: down
      mac:
        address: 86:4c:68:ec:be:8c
    - adPartnerMac: "00:00:00:00:00:00"
      hostNic:
        bootProtocol: none
        bridged: "False"
        customConfiguration: null
        mtu: "1490"
        name: bond1
        options:
        - option:
            name: miimon
            value: "100"
        - option:
            name: mode
            value: "4"
        slaves:
        - hostNic:
            name: dummy_1
        status: up
      mac:
        address: d6:0b:90:af:6c:c5
    - hostNic:
        baseInterface: bond1
        bootProtocol: none
        bridged: "True"
        customConfiguration: null
        mtu: "1490"
        name: bond1.10
        status: up
        vlan:
          id: "10"
    infoStatus:
      Success:
        message: ""
        reason: ""
    networkAttachments:
    - inSync: "true"
      ipAddressAssignments:
        ipAddressAssignment:
        - assignmentMethod: static
          ip:
            address: 10.10.10.2
            netmask: 255.255.255.0
      name: net1
      reportedConfigurations:
        reportedConfiguration:
        - actualValue: "1490"
          expectedValue: "1490"
          inSync: "true"
          name: mtu
        - actualValue: "true"
          expectedValue: "true"
          inSync: "true"
          name: bridged
        - inSync: "true"
          name: vlan
        - actualValue: STATIC
          expectedValue: STATIC
          inSync: "true"
          name: ipv4_boot_protocol
    setupStatus:
      Success:
        message: ""
        reason: ""
kind: List
metadata: {}
resourceVersion: ""
selfLink: ""
```
