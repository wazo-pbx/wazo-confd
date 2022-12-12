# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request
from xivo.tenant_flask_helpers import Tenant
from xivo_dao import tenant_dao

from xivo_dao.alchemy.linefeatures import LineFeatures as Line

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource
from wazo_confd.plugins.line.schema import (
    LineListSchema,
    LinePutSchema,
)

class LineList(ListResource):

    model = Line
    schema = LineListSchema
    has_tenant_uuid = True

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    def build_headers(self, line):
        return {'Location': url_for('lines', id=line['id'], _external=True)}

    @required_acl('confd.lines.read')
    def get(self):
        return super().get()

    @required_acl('confd.lines.create')
    def post(self):
        tenant = Tenant.autodetect()
        tenant_dao.find_or_create_tenant(tenant.uuid)
        tenant_uuids = self._build_tenant_list({'recurse': True})
        resource = self._middleware.create(
            request.get_json(), tenant.uuid, tenant_uuids
        )
        return resource, 201, self.build_headers(resource)


class LineItem(ItemResource):

    # The schema should be the same as the POST once the PUT handle sub-resource updates
    schema = LinePutSchema
    has_tenant_uuid = True

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    @required_acl('confd.lines.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.lines.{id}.update')
    def put(self, id):
        kwargs = self._add_tenant_uuid()
        model = self.service.get(id, **kwargs)
        self.parse_and_update(model, **kwargs)
        return '', 204

    @required_acl('confd.lines.{id}.delete')
    def delete(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.delete(id, tenant_uuids)
        return '', 204
