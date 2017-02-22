# VDSM Network Handler

VDSM host networking controlled by Kubernetes API.

## Warning

- Don't look at the code...
- Don't check out master branch, I'm force pushing!

## Usage

Make sure `openvswitch` and `libvirtd` is installed on all nodes. Also you
need to `modprobe bonding` on node in order to be able to use that kernel
module in containers.

Install `VdsmNetwork`, `VdsmBonding` and `VdsmNetworkAttachment` TPRs and
`DaemonSet` with `vdsm-net-handler` running.

```shell
kubectl apply -f https://raw.githubusercontent.com/phoracek/vdsm-net-handler/master/manifests/add-on.yml
```

And finally apply configuration with logical networks, bondings and per-node
attachments.

```yaml
---
apiVersion: 'ovirt.org/v1alpha1'
kind: VdsmNetwork
metadata:
  name: net1
spec:
  bridged: true
  bonding: bond1
  bootproto: dhcp
  defaultRoute: true
---
apiVersion: 'ovirt.org/v1alpha1'
kind: VdsmNetwork
metadata:
  name: net2
spec:
  bridged: true
  nic: $red
  bootproto: dhcp
---
apiVersion: 'ovirt.org/v1alpha1'
kind: VdsmBonding
metadata:
  name: bond1
spec:
  nics:
    - $blue
    - $green
---
apiVersion: 'ovirt.org/v1alpha1'
kind: VdsmNetworkAttachment
metadata:
  name: node1
spec:
  networks:
    - net1
  bondings:
    - bond1
  labels:
    blue: eth0
    green: eth1
---
apiVersion: 'ovirt.org/v1alpha1'
kind: VdsmNetworkAttachment
metadata:
  name: node2
spec:
  networks:
    - net2
  labels:
    red: eth0
```

Note that removal of `VdsmNetworkAttachment` must be done in two steps, first
remove all networks and bondings from the attachment and only then delete it.