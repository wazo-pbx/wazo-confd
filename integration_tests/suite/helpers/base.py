# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from contextlib import contextmanager
from uuid import uuid4

from wazo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase
from wazo_test_helpers.bus import BusClient
from wazo_test_helpers.auth import (
    MockUserToken,
    MockCredentials,
    AuthClient as MockAuthClient,
)

from .ari import ARIClient
from .auth import AuthClient
from .bus import setup_bus as setup_bus_helpers
from .client import ConfdClient
from .database import create_helper as db_create_helper
from .filesystem import FileSystemClient, TenantFileSystemClient
from .helpers import setup_confd as setup_confd_helpers
from .helpers import setup_database as setup_database_helpers
from .helpers import setup_new_client as setup_new_client_helpers
from .helpers import setup_provd as setup_provd_helpers
from .provd import create_helper as provd_create_helper
from .sysconfd import SysconfdMock
from .wait_strategy import EverythingOkWaitStrategy

from .config import (
    TOKEN,
    TOKEN_SUB_TENANT,
    MAIN_TENANT,
    SUB_TENANT,
    DELETED_TENANT,
    CREATED_TENANT,
    USER_UUID,
)


class IntegrationTest(AssetLaunchingTestCase):
    service = 'confd'
    assets_root = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
    wait_strategy = EverythingOkWaitStrategy()

    @classmethod
    def setup_token(cls):
        cls.mock_auth = MockAuthClient('127.0.0.1', cls.service_port(9497, 'auth'))
        token = MockUserToken(
            TOKEN,
            'user_uuid',
            metadata={'uuid': USER_UUID, 'tenant_uuid': MAIN_TENANT},
        )
        cls.mock_auth.set_token(token)
        token = MockUserToken(
            TOKEN_SUB_TENANT,
            'user_uuid',
            metadata={'uuid': 'user_uuid', 'tenant_uuid': SUB_TENANT},
        )
        cls.mock_auth.set_token(token)
        cls._reset_auth_tenants()

    @classmethod
    def authenticate_user(cls, user) -> str:
        token = MockUserToken(
            str(uuid4()),
            user['uuid'],
            metadata={'uuid': user['uuid'], 'tenant_uuid': SUB_TENANT},
        )
        cls.mock_auth.set_token(token)
        return token.token_id

    @classmethod
    def setup_service_token(cls):
        auth = MockAuthClient('127.0.0.1', cls.service_port(9497, 'auth'))
        credential = MockCredentials('confd-service', 'confd-password')
        auth.set_valid_credentials(credential, str(TOKEN))

    @classmethod
    def sync_db(cls):
        cls.docker_exec(['wazo-confd-sync-db', '--debug'])

    @classmethod
    def purge_meetings(cls):
        cls.docker_exec(['wazo-confd-purge-meetings', '--debug'])

    @classmethod
    def purge_meeting_authorizations(cls):
        return cls.docker_exec(
            ['wazo-confd-purge-meetings', '--debug', '--authorizations-only'],
        )

    @classmethod
    def _create_auth_tenant(cls):
        cls.mock_auth.set_tenants(
            {
                'uuid': MAIN_TENANT,
                'name': 'name1',
                'slug': 'slug1',
                'parent_uuid': MAIN_TENANT,
            },
            {
                'uuid': CREATED_TENANT,
                'name': 'name4',
                'slug': 'slug2',
                'parent_uuid': MAIN_TENANT,
            },
        )

    @classmethod
    def _delete_auth_tenant(cls):
        cls.mock_auth.set_tenants(
            {
                'uuid': MAIN_TENANT,
                'name': 'name1',
                'slug': 'slug1',
                'parent_uuid': MAIN_TENANT,
            },
        )

    @classmethod
    def _reset_auth_tenants(cls):
        cls.mock_auth.set_tenants(
            {
                'uuid': MAIN_TENANT,
                'name': 'name1',
                'slug': 'slug1',
                'parent_uuid': MAIN_TENANT,
            },
            {
                'uuid': SUB_TENANT,
                'name': 'name2',
                'slug': 'slug2',
                'parent_uuid': MAIN_TENANT,
            },
            {
                'uuid': DELETED_TENANT,
                'name': 'name3',
                'slug': 'slug3',
                'parent_uuid': MAIN_TENANT,
            },
            {
                'uuid': CREATED_TENANT,
                'name': 'name4',
                'slug': 'slug4',
                'parent_uuid': MAIN_TENANT,
            },
        )

    @classmethod
    @contextmanager
    def delete_auth_tenant(cls, tenant_uuid):  # tenant_uuid improve readability
        cls._delete_auth_tenant()
        yield
        # NOTE(fblackburn): re-add DELETED_TENANT to be able to make
        # get through API and detect if sync-db doesn't work.
        cls._reset_auth_tenants()

    @classmethod
    @contextmanager
    def create_auth_tenant(cls, tenant_uuid):  # tenant_uuid improve readability
        cls._create_auth_tenant()  # FIXME pass tenant_uuid
        yield
        cls._reset_auth_tenants()

    @classmethod
    def setup_provd(cls, *args, **kwargs):  # args seems needed for IsolatedAction
        helper = cls.create_provd()
        helper.reset()
        return helper

    @classmethod
    def create_provd(cls):
        return provd_create_helper(port=cls.service_port(8666, 'provd'))

    @classmethod
    def setup_database(cls):
        helper = cls.create_database()
        helper.recreate()
        return helper

    @classmethod
    def create_database(cls):
        return db_create_helper(port=cls.service_port(5432, 'postgres'))

    @classmethod
    def setup_sysconfd(cls, *args, **kwargs):  # args seems needed for IsolatedAction
        helper = cls.create_sysconfd()
        helper.clear()
        return helper

    @classmethod
    def setup_auth(cls, *args, **kwargs):
        helper = cls.create_auth()
        helper.clear()
        return helper

    @classmethod
    def create_sysconfd(cls):
        url = 'http://127.0.0.1:{port}'.format(port=cls.service_port(8668, 'sysconfd'))
        return SysconfdMock(url)

    @classmethod
    def setup_helpers(cls):
        setup_confd_helpers(host='127.0.0.1', port=cls.service_port('9486', 'confd'))
        setup_new_client_helpers(
            host='127.0.0.1', port=cls.service_port('9486', 'confd')
        )
        setup_database_helpers(
            host='127.0.0.1', port=cls.service_port(5432, 'postgres')
        )
        setup_provd_helpers(host='127.0.0.1', port=cls.service_port(8666, 'provd'))
        setup_bus_helpers(host='127.0.0.1', port=cls.service_port(5672, 'rabbitmq'))

    @classmethod
    def create_confd(cls, headers=None, encoder=None, user_uuid=None):
        token_id = None
        if user_uuid:
            token = MockUserToken.some_token(
                user_uuid=user_uuid,
                metadata={'uuid': user_uuid, 'tenant_uuid': MAIN_TENANT},
            )
            cls.mock_auth.set_token(token)
            token_id = token.token_id
        client = cls.new_client(headers, encoder, token=token_id)
        return client.url

    @classmethod
    def new_client(cls, headers=None, encoder=None, token=None):
        client = ConfdClient.from_options(
            host='127.0.0.1',
            port=cls.service_port('9486', 'confd'),
            headers=headers,
            encoder=encoder,
            token=token,
        )
        return client

    @classmethod
    def create_bus(cls, exchange_name=None, exchange_type=None):
        port = cls.service_port(5672, 'rabbitmq')
        client = BusClient.from_connection_fields(
            host='127.0.0.1',
            port=port,
            exchange_name=exchange_name,
            exchange_type=exchange_type,
        )
        return client

    @classmethod
    def create_auth(cls):
        return AuthClient(
            host='127.0.0.1',
            port=cls.service_port(9497, 'auth'),
            prefix=None,
            https=False,
        )

    @classmethod
    def create_ari(cls):
        return ARIClient(host='127.0.0.1', port=cls.service_port(5039, 'ari'))

    @classmethod
    def create_filesystem(cls, base_path):
        return FileSystemClient(base_path=base_path, execute=cls.docker_exec)

    @classmethod
    def create_tenant_filesystem(cls, base_path):
        return TenantFileSystemClient(base_path=base_path, execute=cls.docker_exec)
