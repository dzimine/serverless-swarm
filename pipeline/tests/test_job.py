from unittest2 import TestCase
from st2tests.base import BaseActionTestCase

import mock

import job


class ParseMountStringTestCase(TestCase):

    def test_parse_mount_string_service_defaults(self):
        mount = job._parse_mount_string(
            "source=/foo/bar,target=/abc/xyz")
        self.assertEqual(mount['Source'], '/foo/bar')
        self.assertEqual(mount['Target'], '/abc/xyz')
        self.assertEqual(mount['Type'], 'volume')
        # Note(dzimine): blocked by https://github.com/docker/docker-py/issues/1371
        # self.assertEqual(mount['ReadOnly'], False)

    def test_parse_mount_string_service(self):
        mount = job._parse_mount_string(
            "type=bind,src=/foo/bar,dst=/abc/xyz,readonly,propagation=slave")
        self.assertEqual(mount['Source'], '/foo/bar')
        self.assertEqual(mount['Target'], '/abc/xyz')
        self.assertEqual(mount['Type'], 'bind')
        # Note(dzimine): blocked by https://github.com/docker/docker-py/issues/1371
        # self.assertEqual(mount['ReadOnly'], False)
        self.assertEqual(mount['BindOptions']['Propagation'], 'slave')

    def test_parse_mount_string_service_advanced(self):
        mount = job._parse_mount_string(
            "src=/foo/bar,dst=/abc/xyz,ro,volume-label=color1=red,"
            "volume-label='color2=blue'")
        self.assertEqual(mount['Source'], '/foo/bar')
        self.assertEqual(mount['Target'], '/abc/xyz')
        # Note(dzimine): blocked by https://github.com/docker/docker-py/issues/1371
        # self.assertEqual(mount['ReadOnly'], False)
        self.assertDictEqual(
            mount['VolumeOptions']['Labels'],
            {'color1': 'red', 'color2': 'blue'})


class RunJobActionTestCase(BaseActionTestCase):

    action_cls = job.RunJobAction

    @mock.patch('docker.api.APIClient.create_service')
    @mock.patch('docker.api.APIClient.tasks')
    def test_run(self, mock_tasks, mock_create):
        mock_create.return_value = {"ID": "1111"}
        mock_tasks.return_value = [{'ID': '111', 'Status': {'State': 'complete'}}]

        action = self.get_action_instance()
        action.pool_interval = 0
        result = action.run(
            image="alpine", command=None, args=['ping', '192.168.1.1'],
            mounts=["source=/foo/bar,dst=/bar,type=bind", "src=foo,dst=bar"])

        mock_create.assert_called_once_with(mock.ANY, name=result[1]['job'])
        mock_tasks.assert_called_with(filters={'service': '1111'})
