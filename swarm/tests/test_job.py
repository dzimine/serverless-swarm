from unittest2 import TestCase
from unittest2 import skip
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
            mounts=["source=/foo/bar,dst=/bar,type=bind", "src=foo,dst=bar"],
            name="myjob", reserve_cpu=4, reserve_memory=536870912)

        expected = {
            'ContainerSpec': {
                'Args': ['ping', '192.168.1.1'],
                'Command': None,
                'Image': 'alpine',
                'Mounts': [
                    {'Source': '/foo/bar', 'Target': '/bar', 'Type': 'bind', 'ReadOnly': False},
                    {'Source': 'foo', 'Target': 'bar', 'Type': 'volume', 'ReadOnly': False}
                ]

            },
            'RestartPolicy': {'Condition': 'none'},
            'Resources': {'Reservations': {'MemoryBytes': 536870912, 'NanoCPUs': 4}}
        }
        mock_create.assert_called_once_with(expected, name=result[1]['job'])
        mock_tasks.assert_called_with(filters={'service': '1111'})

    @mock.patch('docker.api.APIClient.create_service')
    @mock.patch('docker.api.APIClient.tasks')
    def test_run_with_defaults(self, mock_tasks, mock_create):
        mock_create.return_value = {"ID": "1111"}
        mock_tasks.return_value = [{'ID': '111', 'Status': {'State': 'complete'}}]

        action = self.get_action_instance()
        action.pool_interval = 0
        result = action.run(image="alpine")

        expected = {
            'ContainerSpec': {
                'Image': 'alpine',
                'Command': None,
                'Args': None
            },
            'RestartPolicy': {'Condition': 'none'},
            'Resources': {'Reservations': {'MemoryBytes': None, 'NanoCPUs': None}}
        }
        mock_create.assert_called_once_with(expected, name=result[1]['job'])
        mock_tasks.assert_called_with(filters={'service': '1111'})

    @skip("Only run on real swarm")
    def test_run_real(self):
        image = "pregistry:5000/encode"
        command = None
        args = ["-i/share/li.txt", "-o/share/li.out", "--delay", "10"]
        mounts = ["source=/vagrant/share,dst=/share,type=bind", "src=share,dst=/bar"]

        action = self.get_action_instance()
        result = action.run(
            image=image, command=command, args=args,
            mounts=mounts)
        print result
