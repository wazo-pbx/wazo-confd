# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers import errors

from xivo_confd.helpers.validator import (Validator,
                                          ValidationGroup,
                                          Optional,
                                          UniqueField,
                                          UniqueFieldChanged,
                                          MemberOfSequence)


class DeviceNotAssociated(Validator):

    def __init__(self, line_dao):
        self.line_dao = line_dao

    def validate(self, device):
        lines = self.line_dao.find_all_by(device=device.id)
        if lines:
            ids = tuple(l.id for l in lines)
            raise errors.resource_associated('Device', 'Line',
                                             device_id=device.id, line_ids=ids)


def build_validator(device_dao, line_dao):
    return ValidationGroup(
        common=[
            Optional('plugin',
                     MemberOfSequence('plugin', device_dao.plugins, 'Plugin')
                     ),
            Optional('template_id',
                     MemberOfSequence('template_id', device_dao.device_templates, 'DeviceTemplate')
                     ),
        ],
        create=[
            Optional('mac',
                     UniqueField('mac',
                                 lambda mac: device_dao.find_by(mac=mac),
                                 'Device')
                     ),
        ],
        edit=[
            Optional('mac',
                     UniqueFieldChanged('mac',
                                        device_dao,
                                        'Device')),
        ],
        delete=[
            DeviceNotAssociated(line_dao)
        ],
    )
