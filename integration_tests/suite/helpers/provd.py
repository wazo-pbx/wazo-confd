# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime

from hamcrest import assert_that, equal_to, has_item, starts_with
from wazo_provd_client import Client as ProvdClient
from wazo_provd_client.exceptions import ProvdError

from .config import TOKEN


class ProvdHelper:
    DEFAULT_CONFIGS = [
        {
            'X_type': 'registrar',
            'deletable': True,
            'displayname': 'local',
            'id': 'default',
            'parent_ids': [],
            'proxy_main': '127.0.0.1',
            'raw_config': {'X_key': 'xivo'},
            'registrar_main': '127.0.0.1',
        },
        {
            'X_type': 'internal',
            'id': 'autoprov',
            'parent_ids': ['base', 'defaultconfigdevice'],
            'raw_config': {
                'sccp_call_managers': {'1': {'ip': '127.0.0.1'}},
                'sip_lines': {
                    '1': {
                        'display_name': 'Autoprov',
                        'number': 'autoprov',
                        'password': 'autoprov',
                        'proxy_ip': '127.0.0.1',
                        'registrar_ip': '127.0.0.1',
                        'username': 'apmy3dCQDw',
                    }
                },
            },
            'role': 'autocreate',
        },
        {
            'X_type': 'internal',
            'deletable': True,
            'id': 'base',
            'parent_ids': [],
            'raw_config': {
                'X_xivo_phonebook_ip': '127.0.0.1',
                'ntp_enabled': True,
                'ntp_ip': '127.0.0.1',
            },
        },
        {
            'X_type': 'device',
            'deletable': True,
            'id': 'defaultconfigdevice',
            'label': 'Default config device',
            'parent_ids': [],
            'raw_config': {'ntp_enabled': True, 'ntp_ip': '127.0.0.1'},
        },
        {
            'X_type': 'device',
            'deletable': True,
            'id': 'mockdevicetemplate',
            'parent_ids': ['base'],
            'raw_config': {},
        },
    ]

    def __init__(self, client):
        self.client = client

    @property
    def configs(self):
        return self.client.configs

    @property
    def devices(self):
        return self.client.devices

    @property
    def params(self):
        return self.client.params

    def reset(self):
        self.clean_devices()
        self.clean_configs()
        self.add_default_configs()

    def clean_devices(self):
        for device in self.devices.list()['devices']:
            self.devices.delete(device['id'])

    def clean_configs(self):
        for config in self.configs.list()['configs']:
            self.configs.delete(config['id'])

    def add_default_configs(self):
        for config in self.DEFAULT_CONFIGS:
            self.configs.create(config)

    def add_device_template(self):
        config = {
            'X_type': 'device',
            'deletable': True,
            'label': 'black-label',
            'parent_ids': [],
            'raw_config': {},
        }

        return self.configs.create(config)['id']

    def associate_line_device(self, device_id):
        # line <-> device association is an operation that is currently performed
        # "completely" only by the web-interface -- fake a minimum amount of work here
        config = {'id': device_id, 'parent_ids': [], 'raw_config': {}}
        self.configs.create(config)

        device = self.devices.get(device_id)
        device['config'] = device_id
        self.devices.update(device)

    def assert_config_does_not_exist(self, config_id):
        try:
            self.configs.get(config_id)
        except ProvdError:
            return
        else:
            raise AssertionError('config "{}" exists in wazo-provd'.format(config_id))

    def assert_device_has_autoprov_config(self, device):
        assert_that(device['config'], starts_with('autoprov'))

    def assert_config_use_device_template(self, config, template_id):
        assert_that(config['configdevice'], equal_to(template_id))
        assert_that(config['parent_ids'], has_item(template_id))

    def has_synchronized(self, cls, device_id, timestamp=None):
        timestamp = timestamp or datetime.utcnow()
        line = "Synchronizing device {}".format(device_id)
        output = self.find_provd_logs(cls, timestamp)
        for log in output.split("\n"):
            if line in log:
                return True
        return False

    def updated_count(self, cls, device_id, timestamp=None):
        timestamp = timestamp or datetime.utcnow()
        expected_line = "Updating config {}".format(device_id)
        output = self.find_provd_logs(cls, timestamp)
        count = len([line for line in output.split("\n") if expected_line in line])
        return count

    def find_provd_logs(self, cls, timestamp):
        since = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return cls.service_logs(service_name='provd', since=since)


def create_helper(host='127.0.0.1', port='8666', token=TOKEN):
    client = ProvdClient(host=host, port=port, prefix='', https=False, token=token)
    return ProvdHelper(client)
