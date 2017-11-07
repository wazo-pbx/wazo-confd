# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request
from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError


class UserSchemaUUIDLoad(BaseSchema):
    uuid = fields.String(required=True)
    priority = fields.Integer()


class UsersUUIDSchema(BaseSchema):
    users = fields.Nested(UserSchemaUUIDLoad, many=True, required=True)


class GroupMemberUserItem(ConfdResource):

    schema = UsersUUIDSchema

    def __init__(self, service, group_dao, user_dao):
        super(GroupMemberUserItem, self).__init__()
        self.service = service
        self.group_dao = group_dao
        self.user_dao = user_dao

    @required_acl('confd.groups.{group_id}.members.users.update')
    def put(self, group_id):
        group = self.group_dao.get(group_id)
        form = self.schema().load(request.get_json()).data
        try:
            members = [{'user': self.user_dao.get_by(uuid=user['uuid']),
                        'priority': user.get('priority', priority)}
                       for priority, user in enumerate(form['users'])]
        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self.service.associate_all_users(group, members)
        return '', 204
