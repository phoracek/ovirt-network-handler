# -*- mode: ruby -*-
# vi: set ft=ruby :

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

# This setup requires NFS. In order to use it you either need to temporarily
# stop firewalld or allow NFS on Vagrant network as follows (replace
# $vagrant-libvirt-dev with name of the bridge used by libvirt network):
# $ firewall-cmd --zone FedoraWorkstation --change-interface $vagrant-libvirt-dev
# $ firewall-cmd --zone FedoraWorkstation --permanent --add-service nfs
# $ firewall-cmd --zone FedoraWorkstation --permanent --add-service rpc-bind
# $ firewall-cmd --zone FedoraWorkstation --permanent --add-service mountd
# $ firewall-cmd --zone FedoraWorkstation --permanent --add-port 2049/udp
# $ firewall-cmd --reload

$INSTALL_K8S = <<SCRIPT
echo "Installing Kubernetes."
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=http://yum.kubernetes.io/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg
       https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
EOF
setenforce 0
yum install -y docker kubelet kubeadm kubectl kubernetes-cn
systemctl enable docker && systemctl start docker
systemctl enable kubelet && systemctl start kubelet
SCRIPT

$RESET_K8S_JOIN = <<SCRIPT
echo "Removing previous 'kubeadm join ...' command."
rm -f /vagrant/join_master
SCRIPT

$SETUP_K8S_MASTER = <<SCRIPT
ip=$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/')
token=$(kubeadm token generate)
kubeadm init --token $token --api-advertise-addresses $ip
kubectl apply -f https://git.io/weave-kube
echo "Waiting for all pods to go up."
while [ $(kubectl get pods --all-namespaces --no-headers | grep -c -v Running) != 0 ]; do
  sleep 5 
done
echo "kubeadm join --token $token $ip" > /vagrant/.vagrant/join_master
echo "Waiting for new node to go up."
sleep 60
while [ $(kubectl get pods --all-namespaces --no-headers | grep -c -v Running) != 0 ]; do
  sleep 5 
done
echo "Cluster was successfully inititialized."
SCRIPT

$SETUP_K8S_NODE = <<SCRIPT
echo "Waiting for master to be inititialized."
while ! [ -e /vagrant/.vagrant/join_master ]; do
  sleep 5 
done
sleep 5
echo "Joining cluster."
sh /vagrant/.vagrant/join_master
SCRIPT

$INSTALL_HANDLER_REQUIREMENTS = <<SCRIPT
echo "Installing vdsm-net-handler host dependencies."
yum install -y http://resources.ovirt.org/pub/yum-repo/ovirt-release-master.rpm
yum install -y openvswitch libvirt
systemctl start openvswitch libvirtd
modprobe bonding
SCRIPT

Vagrant.configure("2") do |config|

  config.vm.box = "centos/7"

  if Vagrant.has_plugin?("vagrant-cachier") then
    config.cache.scope = :machine
    config.cache.auto_detect = false
    config.cache.enable :yum
  end

  config.vm.provider "libvirt" do |libvirt|
    libvirt.cpu_mode = 'host-passthrough'
    libvirt.memory = 2048
    libvirt.cpus = 2
  end

  config.vm.synced_folder ".", "/vagrant", type: "nfs"

  config.vm.define "master", primary: true do |master|
    master.vm.box = "centos/7"
    master.vm.hostname = "master"
    master.vm.provision "shell", inline: $RESET_K8S_JOIN
    master.vm.provision "shell", inline: $INSTALL_K8S
    master.vm.provision "shell", inline: $SETUP_K8S_MASTER
    master.vm.provision "shell", inline: $INSTALL_HANDLER_REQUIREMENTS
  end

  config.vm.define "node1" do |node1|
    node1.vm.hostname = "node1"
    node1.vm.provision "shell", inline: $INSTALL_K8S
    node1.vm.provision "shell", inline: $SETUP_K8S_NODE
    node1.vm.provision "shell", inline: $INSTALL_HANDLER_REQUIREMENTS
  end

end