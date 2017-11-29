# -*- coding: UTF-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from collections import OrderedDict

from xivo_confd.plugins.call_permission.service import build_service as build_call_permission_service
from xivo_confd.plugins.endpoint_sccp.service import build_service as build_sccp_service
from xivo_confd.plugins.endpoint_sip.service import build_service as build_sip_service
from xivo_confd.plugins.entity.service import build_service as build_entity_service
from xivo_confd.plugins.extension.service import build_service as build_extension_service
from xivo_confd.plugins.incall.service import build_service as build_incall_service
from xivo_confd.plugins.incall_extension.service import build_service as build_incall_extension_service
from xivo_confd.plugins.line.service import build_service as build_line_service
from xivo_confd.plugins.line_endpoint.service import build_service as build_le_service
from xivo_confd.plugins.line_extension.service import build_service as build_line_extension_service
from xivo_confd.plugins.user.service import build_service as build_user_service
from xivo_confd.plugins.user_call_permission.service import build_service as build_user_call_permission_service
from xivo_confd.plugins.user_cti_profile.service import build_service as build_user_cti_profile_service
from xivo_confd.plugins.user_entity.service import build_service as build_user_entity_service
from xivo_confd.plugins.user_line.service import build_service as build_ul_service
from xivo_confd.plugins.user_voicemail.service import build_service as build_uv_service
from xivo_confd.plugins.voicemail.service import build_service as build_voicemail_service

from xivo_dao.resources.call_permission import dao as call_permission_dao
from xivo_dao.resources.cti_profile import dao as cti_profile_dao
from xivo_dao.resources.endpoint_sccp import dao as sccp_dao
from xivo_dao.resources.endpoint_sip import dao as sip_dao
from xivo_dao.resources.entity import dao as entity_dao
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.user_call_permission import dao as user_call_permission_dao
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.user_voicemail import dao as user_voicemail_dao
from xivo_dao.resources.voicemail import dao as voicemail_dao

from .associators import (
    CallPermissionAssociator,
    CtiProfileAssociator,
    EntityAssociator,
    ExtensionAssociator,
    IncallAssociator,
    LineAssociator,
    SccpAssociator,
    SipAssociator,
    VoicemailAssociator
)
from .creators import (
    CallPermissionCreator,
    CtiProfileCreator,
    EntityCreator,
    ExtensionCreator,
    IncallCreator,
    LineCreator,
    SccpCreator,
    SipCreator,
    UserCreator,
    VoicemailCreator
)
from .entry import EntryCreator, EntryAssociator, EntryFinder, EntryUpdater
from .resource import UserImportResource, UserExportResource
from .service import ImportService


class Plugin(object):

    def load(self, core):
        api = core.api
        provd_client = core.provd_client()

        user_service = build_user_service(provd_client)
        entity_service = build_entity_service()
        user_voicemail_service = build_uv_service()
        user_cti_profile_service = build_user_cti_profile_service()
        voicemail_service = build_voicemail_service()
        line_service = build_line_service(provd_client)
        sip_service = build_sip_service(provd_client)
        sccp_service = build_sccp_service()
        line_sip_service = build_le_service(provd_client, 'sip', sip_service)
        line_sccp_service = build_le_service(provd_client, 'sccp', sccp_service)
        extension_service = build_extension_service(provd_client)
        user_line_service = build_ul_service()
        user_entity_service = build_user_entity_service()
        line_extension_service = build_line_extension_service()
        call_permission_service = build_call_permission_service()
        user_call_permission_service = build_user_call_permission_service()
        incall_service = build_incall_service()
        incall_extension_service = build_incall_extension_service()

        creators = {'user': UserCreator(user_service),
                    'entity': EntityCreator(entity_service),
                    'line': LineCreator(line_service),
                    'voicemail': VoicemailCreator(voicemail_service),
                    'sip': SipCreator(sip_service),
                    'sccp': SccpCreator(sccp_service),
                    'extension': ExtensionCreator(extension_service),
                    'extension_incall': ExtensionCreator(extension_service),
                    'incall': IncallCreator(incall_service),
                    'cti_profile': CtiProfileCreator(cti_profile_dao),
                    'call_permissions': CallPermissionCreator(call_permission_service),
                    }

        entry_creator = EntryCreator(creators)

        associators = OrderedDict([
            ('entity', EntityAssociator(user_entity_service)),
            ('voicemail', VoicemailAssociator(user_voicemail_service)),
            ('cti_profile', CtiProfileAssociator(user_cti_profile_service, cti_profile_dao)),
            ('sip', SipAssociator(line_sip_service)),
            ('sccp', SccpAssociator(line_sccp_service)),
            ('line', LineAssociator(user_line_service)),
            ('extension', ExtensionAssociator(line_extension_service)),
            ('incall', IncallAssociator(incall_extension_service)),
            ('call_permissions', CallPermissionAssociator(user_call_permission_service,
                                                          call_permission_service)),
        ])

        entry_associator = EntryAssociator(associators)

        entry_finder = EntryFinder(user_dao,
                                   entity_dao,
                                   voicemail_dao,
                                   user_voicemail_dao,
                                   cti_profile_dao,
                                   line_dao,
                                   user_line_dao,
                                   line_extension_dao,
                                   sip_dao,
                                   sccp_dao,
                                   extension_dao,
                                   incall_dao,
                                   call_permission_dao,
                                   user_call_permission_dao)

        entry_updater = EntryUpdater(creators, associators, entry_finder)

        service = ImportService(entry_creator, entry_associator, entry_updater)

        api.add_resource(
            UserImportResource,
            '/users/import',
            resource_class_args=(service,)
        )

        api.add_resource(
            UserExportResource,
            '/users/export'
        )
