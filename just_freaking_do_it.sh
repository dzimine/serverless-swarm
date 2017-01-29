#!/bin/bash
echo "Firing up a Swarm cluster with bunch of other cool stuff."
echo "This will take about 30 minutes."
echo "Go get yourself a cup of coffee and come back to enjoy the show."
echo ""
echo ""
echo "Once done, all software will be installed,"
echo "however you'll have to complete some steps inside st2 node."
echo "Check README.md"
echo ""

set -e

DOMAIN=${DOMAIN:-"dev.net"}
IP_BASE=${IP_BASE:-"192.168.88"}
INVENTORY="inventory.${DOMAIN}"

source ./scripts/timer.sh
t=$(timer)

echo -n "Staring up vagrant... "
IP_BASE=$IP_BASE DOMAIN=$DOMAIN vagrant up > vagrant.log
echo "Done!"

echo -n "Installing Docker and Swarm... "
ansible-playbook playbook-swarm.yml  -v -i $INVENTORY > playbook-swarm.log
echo "Done!"

echo -n "Installing local Registry... "
ansible-playbook playbook-registry.yml -v  -i $INVENTORY > playbook-registry.log
echo "Done!"

echo -n "Installing StackStorm... "
ansible-playbook playbook-st2.yml -v -i $INVENTORY > playbook-st2.log
echo "Done!"

printf 'Elapsed time: %s\n' $(timer $t)
