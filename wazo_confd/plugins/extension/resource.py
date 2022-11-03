# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for

from xivo_dao.alchemy.extension import Extension

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import ExtensionSchema


class ExtensionList(ListResource):

    model = Extension
    schema = ExtensionSchema

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    def build_headers(self, extension):
        return {'Location': url_for('extensions', id=extension['id'], _external=True)}

    @required_acl('confd.extensions.read')
    def get(self):
        return super().get()

    @required_acl('confd.extensions.create')
    def post(self):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        resource = self._middleware.create(request.get_json(), tenant_uuids)
        return resource, 201, self.build_headers(resource)

    def _has_a_tenant_uuid(self):
        # The base function does not work because the tenant_uuid is not part
        # of the Extension model and is added by the dao.
        return True


class ExtensionItem(ItemResource):

    schema = ExtensionSchema
    has_tenant_uuid = True

    @required_acl('confd.extensions.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.extensions.{id}.update')
    def put(self, id):
        kwargs = self._add_tenant_uuid()
        model = self.service.get(id, **kwargs)
        self.parse_and_update(model, **kwargs)
        return '', 204

    @required_acl('confd.extensions.{id}.delete')
    def delete(self, id):
        return super().delete(id)
