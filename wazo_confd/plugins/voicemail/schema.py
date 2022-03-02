# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length, Range, Regexp

from wazo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink, Nested
from wazo_confd.helpers.validator import LANGUAGE_REGEX

PASSWORD_REGEX = r"^[0-9]{1,80}$"


class VoicemailSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(validate=Length(max=80), required=True)
    number = fields.Integer(validate=Range(min=0), validate=Length(max=40), required=True)
    context = fields.String(required=True)
    password = fields.String(validate=Regexp(PASSWORD_REGEX), allow_none=True)
    email = fields.String(validate=Length(max=80), allow_none=True)
    language = fields.String(validate=Regexp(LANGUAGE_REGEX), allow_none=True)
    timezone = fields.String(allow_none=True)
    pager = fields.String(validate=Length(max=80), allow_none=True)
    max_messages = fields.Integer(validate=Range(min=0), allow_none=True)
    attach_audio = StrictBoolean(allow_none=True)
    delete_messages = StrictBoolean()
    ask_password = StrictBoolean()
    enabled = StrictBoolean()
    options = fields.List(fields.List(fields.String(), validate=Length(equal=2)))
    links = ListLink(Link('voicemails'))

    users = Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname', 'links'],
        many=True,
        dump_only=True,
    )
