# -*- coding: utf-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+


from marshmallow import fields, post_load, post_dump
from marshmallow.validate import Length, Range, OneOf

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean


class GroupSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Length(max=128), required=True)
    preprocess_subroutine = fields.String(validate=Length(max=39), allow_none=True)
    ring_strategy = fields.String(validate=OneOf([
        'all',
        'random',
        'least_recent',
        'linear',  # Issue when editing to this value: ASTERISK-17049
        'fewest_calls',
        'memorized_round_robin',
        'weight_random'
    ]))
    caller_id_mode = fields.String(validate=OneOf(['prepend', 'overwrite', 'append']), allow_none=True)
    caller_id_name = fields.String(validate=Length(max=80), allow_none=True)
    timeout = fields.Integer(validate=Range(min=0), allow_none=True)
    user_timeout = fields.Integer(validate=Range(min=0), allow_none=True)
    retry_delay = fields.Integer(validate=Range(min=0), allow_none=True)
    music_on_hold = fields.String(validate=Length(max=128), allow_none=True)
    ring_in_use = StrictBoolean()
    enabled = StrictBoolean()
    links = ListLink(Link('groups'))

    extensions = fields.Nested('ExtensionSchema',
                               only=['id', 'exten', 'context', 'links'],
                               many=True,
                               dump_only=True)
    fallbacks = fields.Nested('GroupFallbackSchema',
                              dump_only=True)
    incalls = fields.Nested('IncallSchema',
                            only=['id',
                                  'extensions',
                                  'links'],
                            many=True,
                            dump_only=True)
    users_member = fields.Nested('GroupUsersMemberSchema',
                                 attribute='group_members',
                                 many=True,
                                 dump_only=True)

    @post_dump
    def convert_ring_strategy_to_user(self, data):
        ring_strategy = data.get('ring_strategy', None)
        if ring_strategy == 'ringall':
            data['ring_strategy'] = 'all'
        elif ring_strategy == 'leastrecent':
            data['ring_strategy'] = 'least_recent'
        elif ring_strategy == 'fewestcalls':
            data['ring_strategy'] = 'fewest_calls'
        elif ring_strategy == 'rrmemory':
            data['ring_strategy'] = 'memorized_round_robin'
        elif ring_strategy == 'wrandom':
            data['ring_strategy'] = 'weight_random'
        return data

    @post_dump
    def wrap_users_member(self, data):
        users_member = data.pop('users_member', [])
        if not self.only or 'members' in self.only:
            data['members'] = {'users': users_member}
        return data

    @post_load
    def convert_ring_strategy_to_database(self, data):
        ring_strategy = data.get('ring_strategy', None)
        if ring_strategy == 'all':
            data['ring_strategy'] = 'ringall'
        elif ring_strategy == 'least_recent':
            data['ring_strategy'] = 'leastrecent'
        elif ring_strategy == 'fewest_calls':
            data['ring_strategy'] = 'fewestcalls'
        elif ring_strategy == 'memorized_round_robin':
            data['ring_strategy'] = 'rrmemory'
        elif ring_strategy == 'weight_random':
            data['ring_strategy'] = 'wrandom'
        return data


class GroupUsersMemberSchema(BaseSchema):
    priority = fields.Integer(attribute='position')
    user = fields.Nested('UserSchema',
                         only=['uuid', 'firstname', 'lastname', 'links'],
                         dump_only=True)

    @post_dump(pass_many=True)
    def merge_user_group_member(self, data, many):
        if not many:
            return self.merge_user(data)

        return [self._merge_user(row) for row in data if row.get('user')]

    def _merge_user(self, row):
        user = row.pop('user')
        row['uuid'] = user.get('uuid', None)
        row['firstname'] = user.get('firstname', None)
        row['lastname'] = user.get('lastname', None)
        row['links'] = user.get('links', [])
        return row
