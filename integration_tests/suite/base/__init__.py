# Copyright 2017-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from ..helpers.base import IntegrationTest
from ..helpers.config import TOKEN
from ..helpers.wrappers import IsolatedAction


class BaseIntegrationTest(IntegrationTest):
    asset = 'base'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_token()
        cls.setup_service_token()
        cls.confd = cls.create_confd({'X-Auth-Token': TOKEN})
        cls.wait_strategy.wait(cls)
        cls.setup_provd()
        cls.setup_database()
        cls.setup_helpers()


def setUpModule():
    BaseIntegrationTest.setUpClass()


def tearDownModule():
    BaseIntegrationTest.tearDownClass()


class mocks:
    @classmethod
    class provd(IsolatedAction):

        actions = {'generate': BaseIntegrationTest.setup_provd}

    @classmethod
    class sysconfd(IsolatedAction):

        actions = {'generate': BaseIntegrationTest.setup_sysconfd}


class SingletonProxy:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.func_args = args
        self.func_kwargs = kwargs
        self.obj = None

    def __getattr__(self, name):
        if self.obj is None:
            self.obj = self.func(*self.func_args, **self.func_kwargs)
        return getattr(self.obj, name)

    def __call__(self, *args, **kwargs):
        if self.obj is None:
            self.obj = self.func(*self.func_args, **self.func_kwargs)
        return self.obj(*args, **kwargs)

    def _reset(self):
        self.obj = None


confd = SingletonProxy(BaseIntegrationTest.create_confd)
confd_csv = SingletonProxy(
    BaseIntegrationTest.create_confd,
    {'Accept': 'text/csv; charset=utf-8', 'X-Auth-Token': TOKEN},
)
create_confd = BaseIntegrationTest.create_confd
auth = SingletonProxy(BaseIntegrationTest.create_auth)
ari = SingletonProxy(BaseIntegrationTest.create_ari)
provd = SingletonProxy(BaseIntegrationTest.create_provd)
db = SingletonProxy(BaseIntegrationTest.create_database)
rabbitmq = SingletonProxy(BaseIntegrationTest.create_bus)
sysconfd = SingletonProxy(BaseIntegrationTest.create_sysconfd)

wazo_sound = SingletonProxy(
    BaseIntegrationTest.create_tenant_filesystem, '/var/lib/wazo/sounds'
)
asterisk_sound = SingletonProxy(
    BaseIntegrationTest.create_filesystem, '/usr/share/asterisk/sounds'
)

asterisk_json_doc = SingletonProxy(
    BaseIntegrationTest.create_filesystem,
    '/usr/share/doc/asterisk-doc/json',
)
