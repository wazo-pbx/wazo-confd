# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import CustomItem, CustomList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service_handle = dependencies['service_handle']

        service = build_service()
        service_handle.register('endpoint_custom', service)

        api.add_resource(
            CustomItem,
            '/endpoints/custom/<int:id>',
            endpoint='endpoint_custom',
            resource_class_args=(service,),
        )
        api.add_resource(
            CustomList, '/endpoints/custom', resource_class_args=(service,)
        )
