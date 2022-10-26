# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from marshmallow import fields, validates_schema
from marshmallow.validate import Length, Predicate, Range
from marshmallow.exceptions import ValidationError

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
    endpoint_sip = Nested('EndpointSIPSchema')
    endpoint_sccp = Nested('SccpSchema')
    endpoint_custom = Nested('CustomSchema')
    extensions = Nested('ExtensionSchema', many=True)
    users = Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname', 'links'],
        many=True,
        dump_only=True,
    )

    @validates_schema
    def _validate_only_one_endpoint(self, data, **kwargs):
        nb_endpoint = 0
        if data.get('endpoint_sip'):
            nb_endpoint += 1
        if data.get('endpoint_sccp'):
            nb_endpoint += 1
        if data.get('endpoint_custom'):
            nb_endpoint += 1

        if nb_endpoint > 1:
            raise ValidationError('Only one endpoint should be configured')


class LineSchemaNullable(LineSchema):
    def on_bind_field(self, field_name, field_obj):
        super().on_bind_field(field_name, field_obj)
        nullable_fields = ['provisioning_code', 'position', 'registrar']
        if field_name in nullable_fields:
            field_obj.allow_none = True


class LineListSchema(LineSchemaNullable):
    extensions = Nested(
        'ExtensionSchema',
        only=['id', 'exten', 'context', 'links'],
        many=True,
    )
    endpoint_sip = Nested(
        'EndpointSIPSchema',
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


# Note: PUT still does not support creating/updating endpoints/extensions
class LinePutSchema(LineSchema):
    extensions = Nested('ExtensionSchema', many=True, dump_only=True)
    endpoint_sip = Nested('EndpointSIPSchema', dump_only=True)
    endpoint_sccp = Nested('SccpSchema', dump_only=True)
    endpoint_custom = Nested('CustomSchema', dump_only=True)
