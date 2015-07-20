#!/bin/bash
hostfile=hosts

echo `cat ~/.ssh/id_rsa.pub` > ~/.ssh/authorized_keys

for i in $(cat $hostfile); do
  if [ $i != `hostname` ]; then
    ssh $(whoami)@$i '
      echo "generating ssh key for `hostname`"
      rm -rf ~/.ssh/id_rsa*
      ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa -q -N ""
      echo "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq+kAN8Cj7wlN6K8iFt8Tcz2y9/ks1Bp5+PnMt2baL3D1pfFlrV759PxjpLwwDIUnuACgfvREc02f+51Aa1JjklyS+FbWb98GIKNY8IPq7m3p1DugKexKk0jKX6b81JE0LXYK6XCTTL44Sq0w7jfjbfc4BfN9ku1q5ySVXJfFA9bAF1ByIJ/e+8eiBIZewkOfrBX0vVW2hjpVXyX3lcluHnjkpslttKNUenh3Ui1oulaHoDXy9ArE6Mw/rzOJWfU+b753AVSElUuyYcfl1qTCqGBcpDlxBcdjsI0bLcTRoiMbRd4D94LfP+A/qGR39w29/CMC2tlceUMOkgE6gm6V9w== root@idcisp-datanode-144" > ~/.ssh/authorized_keys
    '
    rm -rf /tmp/sshkey > /dev/null 2>&1
    scp $(whoami)@$i:~/.ssh/id_rsa.pub /tmp/sshkey > /dev/null 2>&1
    echo `cat /tmp/sshkey` >> ~/.ssh/authorized_keys
    rm -rf /tmp/sshkey > /dev/null 2>&1
  fi
done

# dispatch authorized_keys
for i in $(cat $hostfile); do
  if [ $i != `hostname` ]; then
    echo "$i: adding ~/.ssh/authorized_keys"
    scp ~/.ssh/authorized_keys $(whoami)@$i:~/.ssh/ > /dev/null 2>&1
  fi
done

echo "Done!"