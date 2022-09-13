# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from marshmallow import fields, pre_load
from marshmallow.validate import Length, Predicate, Range
from marshmallow.exceptions import ValidationError

from xivo import mallow_helpers as mallow

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, Nested


class LineSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(dump_only=True)
    protocol = fields.String(dump_only=True)
    device_id = fields.String(dump_only=True)
    device_slot = fields.Integer(dump_only=True)
    provisioning_extension = fields.String(dump_only=True)

    context = fields.String(required=True)
    provisioning_code = fields.String(validate=(Predicate('isdigit'), Length(equal=6)))
    position = fields.Integer(validate=Range(min=1))
    caller_id_name = fields.String(
        allow_none=True
    )  # Validate length callerid_name + num = max(160)
    caller_id_num = fields.String(validate=Predicate('isdigit'), allow_none=True)
    registrar = fields.String(validate=Length(max=128))
    links = ListLink(Link('lines'))

    application = Nested(
        'ApplicationSchema', only=['uuid', 'name', 'links'], dump_only=True
    )
    endpoint_sip = Nested(
        'EndpointSIPSchema',
        # TODO(pc-m): Is it really useful to have the username/password on the relation?
        only=[
            'uuid',
            'label',
            'name',
            'auth_section_options.username',
            'links',
        ],
        dump_only=True,
    )
    endpoint_sccp = Nested('SccpSchema', only=['id', 'links'], dump_only=True)
    endpoint_custom = Nested(
        'CustomSchema', only=['id', 'interface', 'links'], dump_only=True
    )
    extensions = Nested(
        'ExtensionSchema',
        only=['id', 'exten', 'context', 'links'],
        many=True,
        dump_only=True,
    )
    users = Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname', 'links'],
        many=True,
        dump_only=True,
    )


class LineSchemaNullable(LineSchema):
    def on_bind_field(self, field_name, field_obj):
        super().on_bind_field(field_name, field_obj)
        nullable_fields = ['provisioning_code', 'position', 'registrar']
        if field_name in nullable_fields:
            field_obj.allow_none = True


class LineSchemaV2(BaseSchema):
    id = mallow.fields.Integer(dump_only=True)
    tenant_uuid = mallow.fields.String(dump_only=True)
    name = mallow.fields.String(dump_only=True)
    protocol = mallow.fields.String(dump_only=True)
    device_id = mallow.fields.String(dump_only=True)
    device_slot = mallow.fields.Integer(dump_only=True)
    provisioning_extension = mallow.fields.String(dump_only=True)

    context = mallow.fields.String(required=True)
    provisioning_code = mallow.fields.String(
        validate=(
            mallow.validate.Predicate('isdigit'),
            mallow.validate.Length(equal=6),
        )
    )
    position = mallow.fields.Integer(validate=mallow.validate.Range(min=1))
    caller_id_name = mallow.fields.String(
        allow_none=True
    )  # Validate length callerid_name + num = max(160)
    caller_id_num = mallow.fields.String(
        validate=mallow.validate.Predicate('isdigit'),
        allow_none=True,
    )
    registrar = mallow.fields.String(validate=mallow.validate.Length(max=128))
    links = ListLink(Link('lines'))

    application = Nested(
        'ApplicationSchema', only=['uuid', 'name', 'links'], dump_only=True
    )
    endpoint_sip = Nested('EndpointSIPSchema')
    endpoint_sccp = Nested('SccpSchema', only=['id', 'links'], dump_only=True)
    endpoint_custom = Nested(
        'CustomSchema', only=['id', 'interface', 'links'], dump_only=True
    )
    extensions = Nested(
        'ExtensionSchema',
        only=['id', 'exten', 'context', 'links'],
        many=True,
    )
    users = Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname', 'links'],
        many=True,
        dump_only=True,
    )

    @pre_load
    def assign_context(self, data, **kwargs):
        if data.get('context'):
            return data

        for extension in data.get('extensions') or []:
            data['context'] = extension['context']
            break

        if not data.get('context'):
            raise ValidationError('A line or it\'s extension need a context')

        return data
