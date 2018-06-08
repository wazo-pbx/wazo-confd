# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from .resource import VoicemailZoneMessagesList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            VoicemailZoneMessagesList,
            '/asterisk/voicemail/zonemessages',
            resource_class_args=(service,)
        )
