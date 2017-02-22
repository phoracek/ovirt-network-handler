FROM centos:7
MAINTAINER Petr Horacek <phoracek@redhat.com>

RUN \
  yum update -y; \
  yum install -y http://resources.ovirt.org/pub/yum-repo/ovirt-release-master.rpm; \
  yum install -y vdsm

RUN yum install -y git python-setuptools python-pbr
COPY ./ vdsm-net-handler/
RUN \
  cd vdsm-net-handler; \
  python setup.py install

CMD \
  modprobe bonding; \
  vdsm-tool dump-bonding-options; \
  vdsm-net-handler
