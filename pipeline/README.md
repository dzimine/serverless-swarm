# Serverless Pipeline Automation Pack

**Note:** this pack is temporary and will be refactored: I'll split it by swarm pack with all swarm st2 actions and sensors, and pipelines pack with all the workflows.

To run the pack's unit tests:

```
# Dang we need ST2
git clone --depth=1 https://github.com/StackStorm/st2.git /tmp/st2
# Run unit tests
ST2_REPO_PATH=/tmp/st2 /opt/stackstorm/st2/bin/st2-run-pack-tests -p /opt/stackstorm/packs/pipeline
```
