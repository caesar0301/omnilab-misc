#!/bin/bash
# Automatically create LVS volume and export it with NFS
# 
# By chenxm
# 2013-07
#
######################
regName="tmp-test"
vol=20GB
######################

## Create new LVM volume and format it using ext4 by default
echo "Creating new LVM volumn..."
echo "Register name: $regName"
echo "Volumn: $vol"
echo "Format: ext4"
echo "Do you wish to create?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) break;;
        No ) exit;;
    esac
done
lvcreate -L $vol -n $regName nova-volumes
mkfs.ext4 /dev/nova-volumes/$regName

## Mount to local /export folder with given name
lp="/export/$regName"
echo "Mount to point: $lp"
echo `mkdir -p $lp`

## Write mount option to /etc/fstab
echo "" >> /etc/fstab
echo "# NFS mounted automatically  at `date`" >> /etc/fstab
echo "/dev/nova-volumes/$regName        $lp     ext4    noatime 0       0" >> /etc/fstab
mount -a

## Add new configuration to /etc/exports
echo "Exporting with NFS..."
echo "" >> /etc/exports
echo "# NFS exported automatically at `date`" >> /etc/exports
echo "/export/$regName 10.50.0.0/20(rw,nohide,insecure,no_subtree_check,async,no_root_squash)" >> /etc/exports

## reload NFS configurations
service nfs reload
