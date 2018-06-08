# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_bus.resources.user_call_permission.event import (
    UserCallPermissionAssociatedEvent,
    UserCallPermissionDissociatedEvent,
)
from xivo_dao.alchemy.rightcall import RightCall as CallPermission
from xivo_dao.alchemy.userfeatures import UserFeatures as User

from ..notifier import UserCallPermissionNotifier


class TestUserCallPermissionNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.call_permission = Mock(CallPermission, id=4)
        self.user = Mock(User, uuid='abcd-1234')

        self.notifier = UserCallPermissionNotifier(self.bus)

    def test_when_call_permission_associate_to_user_then_event_sent_on_bus(self):
        expected_event = UserCallPermissionAssociatedEvent(self.user.uuid, self.call_permission.id)

        self.notifier.associated(self.user, self.call_permission)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_call_permission_dissociate_to_user_then_event_sent_on_bus(self):
        expected_event = UserCallPermissionDissociatedEvent(self.user.uuid, self.call_permission.id)

        self.notifier.dissociated(self.user, self.call_permission)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
