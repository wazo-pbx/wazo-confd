# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_provd_client import Client as ProvdClient

from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao.resources.pjsip_transport import dao as transport_dao

from .resource import SipItem, SipList, SipTemplateItem, SipTemplateList
from .service import build_endpoint_service, build_template_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        provd_client = ProvdClient(**config['provd'])
        token_changed_subscribe(provd_client.set_token)

        endpoint_service = build_endpoint_service(provd_client)
        template_service = build_template_service(provd_client)

        api.add_resource(
            SipItem,
            '/endpoints/sip/<uuid:uuid>',
            endpoint='endpoint_sip',
            resource_class_args=(endpoint_service, transport_dao),
        )
        api.add_resource(
            SipList,
            '/endpoints/sip',
            resource_class_args=(endpoint_service, sip_dao, transport_dao),
        )
        api.add_resource(
            SipTemplateItem,
            '/endpoints/sip/templates/<uuid:uuid>',
            endpoint='endpoint_sip_templates',
            resource_class_args=(template_service, transport_dao),
        )
        api.add_resource(
            SipTemplateList,
            '/endpoints/sip/templates',
            resource_class_args=(template_service, sip_dao, transport_dao),
        )
