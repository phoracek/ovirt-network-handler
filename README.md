# VDSM Network Handler

VDSM host networking controlled by Kubernetes API.

## Warning

- Don't look at the code...
- Don't check out master branch, I'm force pushing!

## Usage

Make sure `openvswitch` and `libvirtd` is installed on all nodes. Also you
need to `modprobe bonding` on node in order to be able to use that kernel
module in containers.

`VdsmNetworkAttachment` TPR and `DaemonSet` with `vdsm-net-handler` running.

```shell
kubectl apply -f https://raw.githubusercontent.com/phoracek/vdsm-net-handler/master/manifests/add-on.yml
```

And finally apply configuration with logical networks, bondings and per-node
attachments.

```yaml
---
apiVersion: 'ovirt.org/v1alpha1'
kind: VdsmNetworkAttachment
metadata:
  name: node1
spec:
  networks:
    net1:
      bridged: true
      bonding: bond1
      bootproto: dhcp
      defaultRoute: true
  bondings:
    bond1:
      nics:
        - eth0
        - eth1
```