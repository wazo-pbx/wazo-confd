# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from .middleware import ExtensionMiddleWare
from .resource import ExtensionItem, ExtensionList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        service = build_service(provd_client)
        extension_middleware = ExtensionMiddleWare(service)

        api.add_resource(
            ExtensionItem,
            '/extensions/<int:id>',
            endpoint='extensions',
            resource_class_args=(service,),
        )
        api.add_resource(
            ExtensionList,
            '/extensions',
            resource_class_args=(
                service,
                extension_middleware,
            ),
        )
