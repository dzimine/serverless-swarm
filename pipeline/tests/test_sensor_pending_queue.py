import mock
from unittest2 import skip
import yaml

from st2tests.base import BaseSensorTestCase

import pending_queue


class SwarmPendingTasksSensorTestCase(BaseSensorTestCase):
    sensor_cls = pending_queue.SwarmPendingTasksSensor

    def setUp(self):
        super(SwarmPendingTasksSensorTestCase, self).setUp()
        self.config = yaml.safe_load(self.get_fixture_content("config.yaml"))

    @mock.patch('docker.api.APIClient.tasks')
    def test_poll_empty(self, mock_tasks):
        mock_tasks.return_value = []
        sensor = self.get_sensor_instance(config=self.config)
        sensor.setup()
        sensor.poll()
        self.assertEqual(self.get_dispatched_triggers(), [])

    @mock.patch('docker.api.APIClient.tasks')
    def test_poll(self, mock_tasks):
        mock_tasks.return_value = [
            {'ID': '111', 'Status': {'State': 'pending'}},
            {'ID': '112', 'Status': {'State': 'pending'}},
            {'ID': '113', 'Status': {'State': 'pending'}},
        ]
        sensor = self.get_sensor_instance()
        sensor.setup()
        sensor.poll()
        self.assertTriggerDispatched(trigger=pending_queue.TRIGGER)
        self.assertEqual(
            self.get_dispatched_triggers()[0]['payload']['count'],
            len(mock_tasks.return_value))
        self.assertEqual(
            self.get_dispatched_triggers()[0]['payload']['tasks'],
            mock_tasks.return_value)
        self.assertEqual(
            self.get_dispatched_triggers()[0]['payload']['over_threshold'], True)
        # Check that trigger dispatch only once
        sensor.poll()
        self.assertEqual(len(self.get_dispatched_triggers()), 1)

    @mock.patch('docker.api.APIClient.tasks')
    def test_going_below_threshlold(self, mock_tasks):
        mock_tasks.return_value = [{'ID': '111', 'Status': {'State': 'pending'}}]
        sensor = self.get_sensor_instance()
        sensor.setup()
        sensor.threshold = 2
        sensor.over_threshold = True
        sensor.poll()
        # print sensor._logger.mock_calls
        self.assertTriggerDispatched(trigger=pending_queue.TRIGGER)
        self.assertEqual(
            self.get_dispatched_triggers()[0]['payload']['over_threshold'], False)

    @mock.patch('docker.api.APIClient.tasks')
    def test_poll_threshold(self, mock_tasks):
        mock_tasks.return_value = [{'ID': '111', 'Status': {'State': 'pending'}}]
        sensor = self.get_sensor_instance(config=self.config)
        sensor.setup()
        sensor.poll()
        self.assertEqual(self.get_dispatched_triggers(), [])

    @skip("Only run on real swarm, with pending tasks")
    def test_poll_real(self):
        sensor = self.get_sensor_instance()
        sensor.setup()
        sensor.poll()
        self.assertTriggerDispatched(trigger=pending_queue.TRIGGER)
        print sensor._logger.mock_calls
