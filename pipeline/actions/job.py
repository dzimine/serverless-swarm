from st2actions.runners.pythonrunner import Action
import random
import time

import docker


def _parse_mount_string(string):
    mount_kwargs = {}
    try:
        fields = string.split(',')
        for field in fields:
            pair = field.split('=', 1)
            key = pair[0]

            if len(pair) == 1:
                if key in ['readonly', 'ro']:
                    mount_kwargs['read_only'] = True
                elif key == 'volume-nocopy':
                    mount_kwargs['no_copy'] = True
                continue

            val = pair[1]
            if key in ['target', 'dst', 'destination']:
                target = val
            elif key in ['source', 'src']:
                source = val
            elif key in ['readonly, ro']:
                mount_kwargs['read_only'] = val
            elif key in ['type', 'propagation']:
                mount_kwargs[key] = val
            elif key == 'volume-label':
                k, v = val.strip("\"\'").split('=')
                mount_kwargs.setdefault('labels', {}).update({k: v})

    except Exception as e:
        raise SyntaxError("Invalid mount format {0}\n{1}".format(string, e))

    return docker.types.Mount(target, source, **mount_kwargs)


class RunJobAction(Action):

    def __init__(self, config):
        super(RunJobAction, self).__init__(config)
        self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        self.pool_interval = 1

    def generate_name(self):
        return "job-" + hex(random.getrandbits(64)).lstrip('0x')

    def run(self, image, command=None, args=None, mounts=None):
        name = self.generate_name()
        self.logger.info("Creating job %s", name)

        # Create service
        try:
            if mounts:
                m = []
                for mount in mounts:
                    m.append(_parse_mount_string(mount))
                mounts = m

            cs = docker.types.ContainerSpec(
                image, command=command, args=args, mounts=mounts)
            tt = docker.types.TaskTemplate(cs, restart_policy={'Condition': 'none'})
            self.logger.debug("TaskTemplate: %s", tt)

            job = self.client.api.create_service(tt, name=name)

            self.logger.info("Job %s created: %s", name, job)

            # NOTE: with `restart-condition=none`, there is only one task.
            #       In general case polling doesn't work well as swarm restart tasks,
            #       keeping 5 latest tasks.

            # Poll for tasks
            while True:
                time.sleep(self.pool_interval)
                tasks = self.client.api.tasks(filters={'service': job['ID']})

                task = tasks[0]
                status = task['Status']
                state = status['State']

                self.logger.debug("Job %s task %s: %s", job['ID'], task['ID'], state)

                if state in ('failed', 'rejected'):
                    self.logger.error(status['Err'])
                    # XXX: remove the job?
                    # self.logger.info("Removing job %s", name)
                    return (False, status['Err'])

                if state == 'complete':
                    break

            # TODO(dzimine): Handle "out of resources" case

        except docker.errors.APIError as e:
            self.logger.error(e)
            return (False, str(e))

        obj = {
            'job': name,
            'image': image,
            'command': command,
            'args': args
        }

        return (True, obj)
