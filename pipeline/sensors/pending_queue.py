from st2reactor.sensor.base import PollingSensor

import docker

TRIGGER = "pipeline.sensor_task_queue"


class SwarmPendingTasksSensor(PollingSensor):
    """
    Swarm pending tasks queue sensor.

    Sensor polls docker swarm for the `pending` tasks
    and dispatches the count and the list
    """

    def __init__(self, sensor_service, config=None, poll_interval=5):
        super(SwarmPendingTasksSensor, self).__init__(sensor_service=sensor_service,
                                                      config=config,
                                                      poll_interval=poll_interval)
        # TODO(dzimine): pass configurable poll_interval from cofig.
        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)

    def setup(self):
        # TODO(dzimine): get url from config
        self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        self.threshold = self._config.get('swarm_pending_tasks_threshold', 0)

    def poll(self):
        tasks = self.client.api.tasks(filters={'desired-state': 'running'})
        pending_tasks = [task for task in tasks if task['Status']['State'] == 'pending']
        pending_count = len(pending_tasks)
        if pending_count > self.threshold:
            payload = {"count": pending_count, "tasks": pending_tasks}
            self._logger.info(
                'SwarmPendingTasksSensor dispatching trigger %s, payload=%s', TRIGGER, payload)
            # TODO: add trace_tag
            self._sensor_service.dispatch(trigger=TRIGGER, payload=payload)

    def cleanup(self):
        # This is called when the st2 system goes down. You can perform cleanup operations like
        # closing the connections to external system here.
        pass

    def add_trigger(self, trigger):
        # This method is called when trigger is created
        pass

    def update_trigger(self, trigger):
        # This method is called when trigger is updated
        pass

    def remove_trigger(self, trigger):
        # This method is called when trigger is deleted
        pass
