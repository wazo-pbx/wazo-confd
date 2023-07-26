# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from ..helpers.filesystem import (
    FileSystemClient,
    TenantFileSystemClient,
)

from ..helpers.client import ConfdClient, RestUrlClient

from ..helpers.database import DbHelper

from ..helpers.provd import ProvdHelper

from ..helpers.ari import ARIClient
from ..helpers.sysconfd import SysconfdMock
from ..helpers.base import IntegrationTest
from ..helpers.config import TOKEN
from ..helpers.wrappers import IsolatedAction
from ..helpers.auth import AuthClient
from wazo_test_helpers.bus import BusClient


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


confd: RestUrlClient = SingletonProxy(BaseIntegrationTest.create_confd)  # type: ignore[assignment]
confd_csv: RestUrlClient = SingletonProxy(
    BaseIntegrationTest.create_confd,
    {'Accept': 'text/csv; charset=utf-8', 'X-Auth-Token': TOKEN},
)  # type: ignore[assignment]
create_confd: ConfdClient = BaseIntegrationTest.create_confd  # type: ignore[assignment]
auth: AuthClient = SingletonProxy(BaseIntegrationTest.create_auth)  # type: ignore[assignment]
ari: ARIClient = SingletonProxy(BaseIntegrationTest.create_ari)  # type: ignore[assignment]
provd: ProvdHelper = SingletonProxy(BaseIntegrationTest.create_provd)  # type: ignore[assignment]
db: DbHelper = SingletonProxy(BaseIntegrationTest.create_database)  # type: ignore[assignment]
rabbitmq: BusClient = SingletonProxy(BaseIntegrationTest.create_bus)  # type: ignore[assignment]
sysconfd: SysconfdMock = SingletonProxy(BaseIntegrationTest.create_sysconfd)  # type: ignore[assignment]


wazo_sound: TenantFileSystemClient = SingletonProxy(
    BaseIntegrationTest.create_tenant_filesystem, '/var/lib/wazo/sounds'
)  # type: ignore[assignment]
asterisk_sound: FileSystemClient = SingletonProxy(
    BaseIntegrationTest.create_filesystem, '/usr/share/asterisk/sounds'
)  # type: ignore[assignment]

asterisk_json_doc: FileSystemClient = SingletonProxy(
    BaseIntegrationTest.create_filesystem,
    '/usr/share/doc/asterisk-doc/json',
)  # type: ignore[assignment]
