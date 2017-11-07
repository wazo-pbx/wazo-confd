# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from flask import url_for

from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import GroupSchema


class GroupList(ListResource):

    model = Group
    schema = GroupSchema

    def build_headers(self, group):
        return {'Location': url_for('groups', id=group.id, _external=True)}

    @required_acl('confd.groups.create')
    def post(self):
        return super(GroupList, self).post()

    @required_acl('confd.groups.read')
    def get(self):
        return super(GroupList, self).get()


class GroupItem(ItemResource):

    schema = GroupSchema

    @required_acl('confd.groups.{id}.read')
    def get(self, id):
        return super(GroupItem, self).get(id)

    @required_acl('confd.groups.{id}.update')
    def put(self, id):
        return super(GroupItem, self).put(id)

    @required_acl('confd.groups.{id}.delete')
    def delete(self, id):
        return super(GroupItem, self).delete(id)
