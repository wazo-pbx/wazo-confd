# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd
from xivo_bus.resources.group_extension.event import (GroupExtensionAssociatedEvent,
                                                      GroupExtensionDissociatedEvent)


class GroupExtensionNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['dialplan reload'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, group, extension):
        self.send_sysconfd_handlers()
        event = GroupExtensionAssociatedEvent(group.id, extension.id)
        self.bus.send_bus_event(event, event.routing_key)

    def dissociated(self, group, extension):
        self.send_sysconfd_handlers()
        event = GroupExtensionDissociatedEvent(group.id, extension.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return GroupExtensionNotifier(bus, sysconfd)
