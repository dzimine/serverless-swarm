# Serverless Pipeline Automation Pack

**Note:** this pack is temporary and will be refactored: I'll split it by swarm pack with all swarm st2 actions and sensors, and pipelines pack with all the workflows.

Don't forget to give `st2` user access to the Docker group `usermod -a -G docker st2`,
else docker won't work.

To run the pack's unit tests:

```
# Activate existing pack's virtual environmet
source /opt/stackstorm/virtualenvs/pipeline/bin/activate
# Run the tests first time - it will install test dependencies
st2-run-pack-tests -x /opt/stackstorm/pipeline
# Skip installing dependencies on subsequent runs
st2-run-pack-tests -x -j /opt/stackstorm/pipeline
```
