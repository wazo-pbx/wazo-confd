# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from .resource import LineItem, LineList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']
        service_handle = dependencies['service_handle']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        service = build_service(provd_client)

        api.add_resource(
            LineItem,
            '/lines/<int:id>',
            endpoint='lines',
            resource_class_args=(service,),
        )
        api.add_resource(LineList, '/lines', resource_class_args=(service, service_handle))
