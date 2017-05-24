import docker
from st2actions.runners.pythonrunner import Action


class PendingQueueAction(Action):

    def __init__(self, config):
        super(PendingQueueAction, self).__init__(config)
        self.client = docker.DockerClient(
            self.config.get('base_url', 'unix://var/run/docker.sock'))

    def run(self):
        try:

            tasks = self.client.api.tasks(filters={'desired-state': 'running'})
            pending_tasks = [task for task in tasks if task['Status']['State'] == 'pending']
            return (True, {'result': {'pending_count': len(pending_tasks)}})
        except Exception as e:
            return (False, str(e))
