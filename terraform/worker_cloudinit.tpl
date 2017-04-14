#cloud-init
#
# Warning! Modifying this template can cause instance re-creation!
#
# Docs: http://cloudinit.readthedocs.io/en/latest/topics/examples.html
# Examples: https://github.com/number5/cloud-init/blob/master/doc/examples/cloud-config.txt
# `cloud-init` will run on startup, see logs in /var/log/cloud-init.log


# Enable ssh as root
disable_root: false

package_upgrade: true
packages:
- nfs-common

runcmd:
- echo "HelloFromTerraform!"
- mkdir -p /mnt/share
- chown ubuntu:ubuntu /mnt/share
- echo "${efs}:/ /mnt/share nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 0 0" >> /etc/fstab
- mkdir -p /mnt/data
- chown ubuntu:ubuntu /mnt/data
- echo "/dev/xvdb /mnt/data    ext4    defaults,nofail   0  2" >> /etc/fstab
- mount -a
# Avoid irritating ssh disconnect
- echo "ClientAliveInterval 60" >>  /etc/ssh/sshd_config
# Leave docker swarm cluster if already joined
- docker swarm leave
- docker swarm join --token $(cat /var/tmp/swarm_worker_token)
