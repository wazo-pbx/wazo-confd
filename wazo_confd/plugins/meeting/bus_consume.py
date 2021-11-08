# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

logger = logging.getLogger(__name__)


class MeetingBusEventHandler:
    def __init__(self, service, notifier):
        self._service = service
        self._notifier = notifier

    def subscribe(self, bus_consumer):
        bus_consumer.on_event(
            'request_handlers_progress', self.on_request_handlers_progress
        )

    def on_request_handlers_progress(self, event):
        for meeting in self._extract_meetings_from_reload_complete(event):
            meeting_uuid = meeting['uuid']
            logger.debug(
                'Meeting %s: reload completed, sending event ready', meeting_uuid
            )
            meeting = self._service.get_by(uuid=meeting_uuid)
            self._notifier.ready(meeting)

    @staticmethod
    def _extract_meetings_from_reload_complete(event):
        for request_context in event.get('context', []):
            if (
                request_context.get('resource_type') == 'meeting'
                and request_context.get('resource_action') != 'deleted'
                and event['status'] == 'completed'
            ):
                yield request_context['resource_body']
