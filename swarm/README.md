# Docker Swarm integration pack (WIP)

Currently, the pack implements a "job" on top of docker "Swarm" service,
and contains sensor and rules for auto-scaling Swarm cluster
on top of AWS and OpenStack.

    TODO: add `docker service`, `docker swarm`, and `docker node` actions.


    TODO: consider moving scale-swarm automation to a separate automation pack.

**Note:** Don't forget to give `st2` user access to the Docker group `usermod -a -G docker st2`,
else docker won't work.

To run the pack's unit tests:

```
# Activate existing pack's virtual environmet
source /opt/stackstorm/virtualenvs/swarm/bin/activate
# Run the tests first time - it will install test dependencies
st2-run-pack-tests -x /opt/stackstorm/swarm
# Skip installing dependencies on subsequent runs
st2-run-pack-tests -x -j /opt/stackstorm/swarm
```
