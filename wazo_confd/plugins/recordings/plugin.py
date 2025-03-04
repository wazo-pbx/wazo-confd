# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .resource import RecordingsAnnouncementsResource
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']

        service = build_service()

        api.add_resource(
            RecordingsAnnouncementsResource,
            '/recordings/announcements',
            resource_class_args=(service,),
        )
