# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.extension_feature.event import EditExtensionFeatureEvent

from wazo_confd import bus, sysconfd


class ExtensionFeatureNotifier:
    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx, 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, extension, updated_fields):
        event = EditExtensionFeatureEvent(extension.id)
        headers = self._build_headers(extension)
        self.bus.send_bus_event(event, headers=headers)
        if updated_fields:
            self.send_sysconfd_handlers(['dialplan reload'])

    def _build_headers(self, extension):
        return {'tenant_uuid': str(extension.tenant_uuid)}


def build_notifier():
    return ExtensionFeatureNotifier(sysconfd, bus)
