from st2reactor.sensor.base import PollingSensor

import docker

TRIGGER = "swarm.pending_tasks"


class SwarmPendingTasksSensor(PollingSensor):
    """
    Swarm pending tasks queue sensor.

    Sensor polls docker swarm for the `pending` tasks
    and dispatches the count and the list
    """

    def __init__(self, sensor_service, config=None):
        super(SwarmPendingTasksSensor, self).__init__(sensor_service=sensor_service,
                                                      config=config)
        self.poll_interval = config.get('poll_interval', 5) if config else 5
        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)
        self.over_threshold = False

    def setup(self):
        self.client = docker.DockerClient(base_url=self.config.get('base_url'))
        self.threshold = self._config.get('swarm_pending_tasks_threshold', 0)

    def poll(self):
        tasks = self.client.api.tasks(filters={'desired-state': 'running'})
        pending_tasks = [task for task in tasks if task['Status']['State'] == 'pending']
        pending_count = len(pending_tasks)

        def _payload():
            return {
                "count": pending_count,
                "over_threshold": self.over_threshold,
                "tasks": pending_tasks
            }

        if not self.over_threshold and pending_count > self.threshold:
            self.over_threshold = True
            self._logger.info(
                'Dispatching trigger %s, UP ABOVE threshold, payload=%s', TRIGGER, _payload())
            # TODO: add trace_tag
            self._sensor_service.dispatch(trigger=TRIGGER, payload=_payload())
        elif self.over_threshold and pending_count <= self.threshold:
            self.over_threshold = False
            self._logger.info(
                'Dispatching trigger %s, DOWN BELOW threshold, payload=%s', TRIGGER, _payload())
            self._sensor_service.dispatch(trigger=TRIGGER, payload=_payload())
        else:
            self._logger.debug(
                'Not dispatching trigger %s: over=%s threshold=%d count=%d ',
                TRIGGER, self.over_threshold, self.threshold, pending_count)

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
