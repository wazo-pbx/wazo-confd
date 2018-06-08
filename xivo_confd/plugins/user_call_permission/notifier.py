# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.user_call_permission.event import (
    UserCallPermissionAssociatedEvent,
    UserCallPermissionDissociatedEvent,
)

from xivo_confd import bus


class UserCallPermissionNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated(self, user, call_permission):
        event = UserCallPermissionAssociatedEvent(user.uuid, call_permission.id)
        self.bus.send_bus_event(event)

    def dissociated(self, user, call_permission):
        event = UserCallPermissionDissociatedEvent(user.uuid, call_permission.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return UserCallPermissionNotifier(bus)
