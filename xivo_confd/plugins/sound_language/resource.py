# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields
from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ListResource


class SoundLanguageSchema(BaseSchema):
    tag = fields.String(dump_only=True)


class SoundLanguageList(ListResource):

    schema = SoundLanguageSchema

    @required_acl('confd.sounds.languages.get')
    def get(self):
        return super(SoundLanguageList, self).get()

    def post(self, id):
        return '', 405
