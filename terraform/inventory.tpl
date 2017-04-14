[targets]
${manager}
${nodes}

[targets:vars]
ansible_user=root
target=aws

[docker_engine]
node[1:${node_count}]
st2

[docker_swarm_manager]
st2

[docker_swarm_worker]
node[1:${node_count}]

[docker_registry]
st2