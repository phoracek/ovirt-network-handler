# oVirt Node Network Handler

Dockerfile: https://github.com/ovirt/ovirt-containers/blob/devel/image-specifications/node-network-handler/Dockerfile

Manifest: https://github.com/ovirt/ovirt-containers/blob/master/os-manifests/node/network-handler-deployment.yaml

Object example:

```yaml
apiVersion: ovirt.org/v1alpha1
kind: OvirtNodeNetwork
metadata:
  creationTimestamp: 2017-04-03T16:04:36Z
  name: dev-17
  namespace: ovirt
  resourceVersion: "36271"
  selfLink: /apis/ovirt.org/v1alpha1/namespaces/ovirt/ovirtnodenetworks/dev-17
  uid: 3c2d1ea6-1887-11e7-8d3b-fe54003b4a9f
spec:
  networks:
    net1:
      bootproto: dhcp
      defaultRoute: true
      nic: enp5s0f0
state:
  capabilities:
    bondings:
      JYcKjIGIXowhetr:
        active_slave: ""
        addr: ""
        dhcpv4: false
        dhcpv6: false
        gateway: ""
        hwaddr: 01:23:45:67:89:ab
        ipv4addrs: []
        ipv4defaultroute: false
        ipv6addrs: []
        ipv6autoconf: true
        ipv6gateway: '::'
        mtu: "1500"
        netmask: ""
        opts:
          mode: "4"
        slaves: []
        switch: legacy
      bond0:
        active_slave: ""
        addr: ""
        dhcpv4: false
        dhcpv6: false
        gateway: ""
        hwaddr: 01:23:45:67:89:ab
        ipv4addrs: []
        ipv4defaultroute: false
        ipv6addrs: []
        ipv6autoconf: true
        ipv6gateway: '::'
        mtu: "1500"
        netmask: ""
        opts:
          mode: "0"
        slaves: []
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
          bridge_id: 8000.0242864ad69f
          default_pvid: "1"
          forward_delay: "1500"
          gc_timer: "6852"
          group_addr: 1:80:c2:0:0:0
          group_fwd_mask: "0x0"
          hash_elasticity: "4"
          hash_max: "512"
          hello_time: "200"
          hello_timer: "0"
          max_age: "2000"
          multicast_last_member_count: "2"
          multicast_last_member_interval: "100"
          multicast_membership_interval: "26000"
          multicast_querier: "0"
          multicast_querier_interval: "25500"
          multicast_query_interval: "12500"
          multicast_query_response_interval: "1000"
          multicast_query_use_ifaddr: "0"
          multicast_router: "1"
          multicast_snooping: "1"
          multicast_startup_query_count: "2"
          multicast_startup_query_interval: "3125"
          multicast_stats_enabled: "0"
          nf_call_arptables: "0"
          nf_call_ip6tables: "0"
          nf_call_iptables: "0"
          priority: "32768"
          root_id: 8000.0242864ad69f
          root_path_cost: "0"
          root_port: "0"
          stp_state: "0"
          tcn_timer: "0"
          topology_change: "0"
          topology_change_detected: "0"
          topology_change_timer: "0"
          vlan_filtering: "0"
          vlan_protocol: "0x8100"
          vlan_stats_enabled: "0"
        ports:
        - vetha5ef97a
        - vethcd02107
        stp: "off"
      net1:
        addr: 10.34.63.177
        dhcpv4: true
        dhcpv6: false
        gateway: 10.34.63.254
        ipv4addrs:
        - 10.34.63.177/22
        ipv4defaultroute: true
        ipv6addrs: []
        ipv6autoconf: false
        ipv6gateway: '::'
        mtu: "1500"
        netmask: 255.255.252.0
        opts:
          ageing_time: "30000"
          bridge_id: 8000.80c16e6c5154
          default_pvid: "1"
          forward_delay: "0"
          gc_timer: "0"
          group_addr: 1:80:c2:0:0:0
          group_fwd_mask: "0x0"
          hash_elasticity: "4"
          hash_max: "512"
          hello_time: "200"
          hello_timer: "0"
          max_age: "2000"
          multicast_last_member_count: "2"
          multicast_last_member_interval: "100"
          multicast_membership_interval: "26000"
          multicast_querier: "0"
          multicast_querier_interval: "25500"
          multicast_query_interval: "12500"
          multicast_query_response_interval: "1000"
          multicast_query_use_ifaddr: "0"
          multicast_router: "1"
          multicast_snooping: "1"
          multicast_startup_query_count: "2"
          multicast_startup_query_interval: "3125"
          multicast_stats_enabled: "0"
          nf_call_arptables: "0"
          nf_call_ip6tables: "0"
          nf_call_iptables: "0"
          priority: "32768"
          root_id: 8000.80c16e6c5154
          root_path_cost: "0"
          root_port: "0"
          stp_state: "0"
          tcn_timer: "0"
          topology_change: "0"
          topology_change_detected: "0"
          topology_change_timer: "0"
          vlan_filtering: "0"
          vlan_protocol: "0x8100"
          vlan_stats_enabled: "0"
        ports:
        - enp5s0f0
        stp: "off"
      virbr0:
        addr: 192.168.122.1
        dhcpv4: false
        dhcpv6: false
        gateway: ""
        ipv4addrs:
        - 192.168.122.1/24
        ipv4defaultroute: false
        ipv6addrs: []
        ipv6autoconf: false
        ipv6gateway: '::'
        mtu: "1500"
        netmask: 255.255.255.0
        opts:
          ageing_time: "30000"
          bridge_id: 8000.525400e73c15
          default_pvid: "1"
          forward_delay: "200"
          gc_timer: "18452"
          group_addr: 1:80:c2:0:0:0
          group_fwd_mask: "0x0"
          hash_elasticity: "4"
          hash_max: "512"
          hello_time: "200"
          hello_timer: "152"
          max_age: "2000"
          multicast_last_member_count: "2"
          multicast_last_member_interval: "100"
          multicast_membership_interval: "26000"
          multicast_querier: "0"
          multicast_querier_interval: "25500"
          multicast_query_interval: "12500"
          multicast_query_response_interval: "1000"
          multicast_query_use_ifaddr: "0"
          multicast_router: "1"
          multicast_snooping: "1"
          multicast_startup_query_count: "2"
          multicast_startup_query_interval: "3125"
          multicast_stats_enabled: "0"
          nf_call_arptables: "0"
          nf_call_ip6tables: "0"
          nf_call_iptables: "0"
          priority: "32768"
          root_id: 8000.525400e73c15
          root_path_cost: "0"
          root_port: "0"
          stp_state: "1"
          tcn_timer: "0"
          topology_change: "0"
          topology_change_detected: "0"
          topology_change_timer: "0"
          vlan_filtering: "0"
          vlan_protocol: "0x8100"
          vlan_stats_enabled: "0"
        ports:
        - vnet0
        - virbr0-nic
        stp: "on"
      virbr1:
        addr: 192.168.42.1
        dhcpv4: false
        dhcpv6: false
        gateway: ""
        ipv4addrs:
        - 192.168.42.1/24
        ipv4defaultroute: false
        ipv6addrs: []
        ipv6autoconf: false
        ipv6gateway: '::'
        mtu: "1500"
        netmask: 255.255.255.0
        opts:
          ageing_time: "30000"
          bridge_id: 8000.52540080036f
          default_pvid: "1"
          forward_delay: "200"
          gc_timer: "11453"
          group_addr: 1:80:c2:0:0:0
          group_fwd_mask: "0x0"
          hash_elasticity: "4"
          hash_max: "512"
          hello_time: "200"
          hello_timer: "153"
          max_age: "2000"
          multicast_last_member_count: "2"
          multicast_last_member_interval: "100"
          multicast_membership_interval: "26000"
          multicast_querier: "0"
          multicast_querier_interval: "25500"
          multicast_query_interval: "12500"
          multicast_query_response_interval: "1000"
          multicast_query_use_ifaddr: "0"
          multicast_router: "1"
          multicast_snooping: "1"
          multicast_startup_query_count: "2"
          multicast_startup_query_interval: "3125"
          multicast_stats_enabled: "0"
          nf_call_arptables: "0"
          nf_call_ip6tables: "0"
          nf_call_iptables: "0"
          priority: "32768"
          root_id: 8000.52540080036f
          root_path_cost: "0"
          root_port: "0"
          stp_state: "1"
          tcn_timer: "0"
          topology_change: "0"
          topology_change_detected: "0"
          topology_change_timer: "0"
          vlan_filtering: "0"
          vlan_protocol: "0x8100"
          vlan_stats_enabled: "0"
        ports:
        - virbr1-nic
        - vnet1
        stp: "on"
    nameservers:
    - 10.34.63.202
    - 10.34.63.204
    networks:
      net1:
        addr: 10.34.63.177
        bridged: true
        dhcpv4: true
        dhcpv6: false
        gateway: 10.34.63.254
        iface: net1
        ipv4addrs:
        - 10.34.63.177/22
        ipv4defaultroute: true
        ipv6addrs: []
        ipv6autoconf: false
        ipv6gateway: '::'
        mtu: "1500"
        netmask: 255.255.252.0
        ports:
        - enp5s0f0
        stp: "off"
        switch: legacy
    nics:
      dummy_1:
        addr: ""
        dhcpv4: false
        dhcpv6: false
        gateway: ""
        hwaddr: 01:23:45:67:89:ab
        ipv4addrs: []
        ipv4defaultroute: false
        ipv6addrs: []
        ipv6autoconf: false
        ipv6gateway: '::'
        mtu: "1500"
        netmask: ""
        speed: 0
      enp5s0f0:
        addr: 10.34.63.177
        dhcpv4: true
        dhcpv6: false
        gateway: 10.34.63.254
        hwaddr: 01:23:45:67:89:ab
        ipv4addrs:
        - 10.34.63.177/22
        ipv4defaultroute: true
        ipv6addrs: []
        ipv6autoconf: false
        ipv6gateway: '::'
        mtu: "1500"
        netmask: 255.255.252.0
        speed: 1000
      enp5s0f1:
        addr: ""
        dhcpv4: false
        dhcpv6: false
        gateway: ""
        hwaddr: 01:23:45:67:89:ab
        ipv4addrs: []
        ipv4defaultroute: false
        ipv6addrs: []
        ipv6autoconf: false
        ipv6gateway: '::'
        mtu: "1500"
        netmask: ""
        speed: 0
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
  statistics: {}
```

## TODO

- source routing
- statistics
