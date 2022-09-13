# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from xivo_dao.alchemy.linefeatures import LineFeatures as Line

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource
from wazo_confd.plugins.line.schema import LineSchema, LineSchemaNullable


class LineList(ListResource):

    model = Line
    schema = LineSchemaNullable
    has_tenant_uuid = True

    def build_headers(self, line):
        return {'Location': url_for('lines', id=line.id, _external=True)}

    @required_acl('confd.lines.read')
    def get(self):
        return super().get()

    @required_acl('confd.lines.create')
    def post(self):
        if self._many:
            body = self.find_json_sub_dict(self.json_path, request.get_json())
        else:
            body = [self.find_json_sub_dict(self.json_path, request.get_json())]

        results = []
        headers = None
        for item in body:
            form = self.schema().load(item)
            model = self.model(**form)
            tenant_uuids = self._build_tenant_list({'recurse': True})
            model = self.service.create(model, tenant_uuids)
            results.append(self.schema().dump(model))
            if not headers:
                headers = self.build_headers(model)

        if self._many:
            return results, 201, headers
        else:
            return results[0], 201, headers


class LineItem(ItemResource):

    schema = LineSchema
    has_tenant_uuid = True

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
        return super().delete(id)
