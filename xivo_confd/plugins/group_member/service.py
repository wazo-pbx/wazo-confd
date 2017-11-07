# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from .notifier import build_notifier
from .validator import build_validator

from xivo_dao.resources.group import dao as group_dao


class GroupMemberUserService(object):

    def __init__(self, group_dao, notifier, validator):
        self.group_dao = group_dao
        self.validator = validator
        self.notifier = notifier

    def associate_all_users(self, group, users):
        self.validator.validate_association(group, users)
        self.group_dao.associate_all_member_users(group, users)
        self.notifier.associated(group, users)


def build_service():
    return GroupMemberUserService(group_dao,
                                  build_notifier(),
                                  build_validator())
