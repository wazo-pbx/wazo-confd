# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.context.event import (
    CreateContextEvent,
    DeleteContextEvent,
    EditContextEvent,
)

from xivo_confd import bus, sysconfd

from .schema import ContextSchema

CONTEXT_FIELDS = [
    'id',
    'name',
    'type',
    'tenant_uuid',
]


class ContextNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': ['dialplan reload'],
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, context):
        self.send_sysconfd_handlers()
        context_serialized = ContextSchema(only=CONTEXT_FIELDS).dump(context).data
        event = CreateContextEvent(**context_serialized)
        self.bus.send_bus_event(event)

    def edited(self, context):
        self.send_sysconfd_handlers()
        context_serialized = ContextSchema(only=CONTEXT_FIELDS).dump(context).data
        event = EditContextEvent(**context_serialized)
        self.bus.send_bus_event(event)

    def deleted(self, context):
        self.send_sysconfd_handlers()
        context_serialized = ContextSchema(only=CONTEXT_FIELDS).dump(context).data
        event = DeleteContextEvent(**context_serialized)
        self.bus.send_bus_event(event)


def build_notifier():
    return ContextNotifier(bus, sysconfd)
