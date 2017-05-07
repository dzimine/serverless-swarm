# Serverless Pipeline Automation Pack

**Note:** this pack is temporary and will be refactored: I'll split it by swarm pack with all swarm st2 actions and sensors, and pipelines pack with all the workflows.

To run the pack's unit tests:

```
# Activate existing pack's virtual environmet
source /opt/stackstorm/virtualenvs/pipeline/bin/activate
# Run the tests first time - it will install test dependencies
t2-run-pack-tests -x /opt/stackstorm/pipeline
# Skip installing dependencies on subsequent runs
t2-run-pack-tests -x -j /opt/stackstorm/pipeline
```
