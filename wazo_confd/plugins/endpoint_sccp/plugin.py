# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .service import build_service
from .resource import SccpItem, SccpList


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service_handle = dependencies['service_handle']

        service = build_service()
        service_handle.register('endpoint_sccp', service)

        api.add_resource(
            SccpItem,
            '/endpoints/sccp/<int:id>',
            endpoint='endpoint_sccp',
            resource_class_args=(service,),
        )
        api.add_resource(SccpList, '/endpoints/sccp', resource_class_args=(service,))
