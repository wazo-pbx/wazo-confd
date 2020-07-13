# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .wrappers import IsolatedAction
from . import helpers as h


class user(IsolatedAction):

    actions = {'generate': h.user.generate_user, 'delete': h.user.delete_user}


class line(IsolatedAction):

    actions = {'generate': h.line.generate_line, 'delete': h.line.delete_line}


class line_sip(IsolatedAction):

    actions = {
        'generate': h.line_sip.generate_line_sip,
        'delete': h.line_sip.delete_line_sip,
    }


class sip(IsolatedAction):

    id_field = 'uuid'
    actions = {
        'generate': h.endpoint_sip.generate_sip,
        'delete': h.endpoint_sip.delete_sip,
    }


class sccp(IsolatedAction):

    actions = {
        'generate': h.endpoint_sccp.generate_sccp,
        'delete': h.endpoint_sccp.delete_sccp,
    }


class extension(IsolatedAction):

    actions = {
        'generate': h.extension.generate_extension,
        'delete': h.extension.delete_extension,
    }


class device(IsolatedAction):

    actions = {'generate': h.device.generate_device, 'delete': h.device.delete_device}


class autoprov(IsolatedAction):

    actions = {'generate': h.device.generate_autoprov, 'delete': h.device.delete_device}


class voicemail(IsolatedAction):

    actions = {
        'generate': h.voicemail.generate_voicemail,
        'delete': h.voicemail.delete_voicemail,
    }


class context(IsolatedAction):

    actions = {
        'generate': h.context.generate_context,
        'delete': h.context.delete_context,
    }


class csv_entry(IsolatedAction):

    actions = {'generate': h.user_import.generate_entry}


class custom(IsolatedAction):

    actions = {
        'generate': h.endpoint_custom.generate_custom,
        'delete': h.endpoint_custom.delete_custom,
    }


class registrar(IsolatedAction):

    actions = {
        'generate': h.registrar.generate_registrar,
        'delete': h.registrar.delete_registrar,
    }


class call_permission(IsolatedAction):

    actions = {
        'generate': h.call_permission.generate_call_permission,
        'delete': h.call_permission.delete_call_permission,
    }


class agent(IsolatedAction):

    actions = {'generate': h.agent.generate_agent, 'delete': h.agent.delete_agent}


class funckey_template(IsolatedAction):

    actions = {
        'generate': h.funckey_template.generate_funckey_template,
        'delete': h.funckey_template.delete_funckey_template,
    }


class call_pickup(IsolatedAction):

    actions = {
        'generate': h.call_pickup.generate_call_pickup,
        'delete': h.call_pickup.delete_call_pickup,
    }


class call_filter(IsolatedAction):

    actions = {
        'generate': h.call_filter.generate_call_filter,
        'delete': h.call_filter.delete_call_filter,
    }


class schedule(IsolatedAction):

    actions = {
        'generate': h.schedule.generate_schedule,
        'delete': h.schedule.delete_schedule,
    }


class queue(IsolatedAction):

    actions = {'generate': h.queue.generate_queue, 'delete': h.queue.delete_queue}


class trunk(IsolatedAction):

    actions = {'generate': h.trunk.generate_trunk, 'delete': h.trunk.delete_trunk}


class incall(IsolatedAction):

    actions = {'generate': h.incall.generate_incall, 'delete': h.incall.delete_incall}


class meetme(IsolatedAction):

    actions = {
        'generate': h.meetme.generate_conference,
        'delete': h.meetme.delete_conference,
    }


class group(IsolatedAction):

    actions = {'generate': h.group.generate_group, 'delete': h.group.delete_group}


class outcall(IsolatedAction):

    actions = {
        'generate': h.outcall.generate_outcall,
        'delete': h.outcall.delete_outcall,
    }


class ivr(IsolatedAction):

    actions = {'generate': h.ivr.generate_ivr, 'delete': h.ivr.delete_ivr}


class agent_login_status(IsolatedAction):

    actions = {
        'generate': h.agent_login_status.generate_agent_login_status,
        'delete': h.agent_login_status.delete_agent_login_status,
    }


class conference(IsolatedAction):

    actions = {
        'generate': h.conference.generate_conference,
        'delete': h.conference.delete_conference,
    }


class parking_lot(IsolatedAction):

    actions = {
        'generate': h.parking_lot.generate_parking_lot,
        'delete': h.parking_lot.delete_parking_lot,
    }


class paging(IsolatedAction):

    actions = {'generate': h.paging.generate_paging, 'delete': h.paging.delete_paging}


class switchboard(IsolatedAction):

    id_field = 'uuid'
    actions = {
        'generate': h.switchboard.generate_switchboard,
        'delete': h.switchboard.delete_switchboard,
    }


class moh(IsolatedAction):

    id_field = 'uuid'
    actions = {'generate': h.moh.generate_moh, 'delete': h.moh.delete_moh}


class voicemail_zonemessages(IsolatedAction):

    actions = {'generate': h.voicemail_zonemessages.generate_voicemail_zonemessages}


class register_sip(IsolatedAction):

    actions = {
        'generate': h.register_sip.generate_register_sip,
        'delete': h.register_sip.delete_register_sip,
    }


class register_iax(IsolatedAction):

    actions = {
        'generate': h.register_iax.generate_register_iax,
        'delete': h.register_iax.delete_register_iax,
    }


class sound(IsolatedAction):

    id_field = 'name'
    actions = {'generate': h.sound.generate_sound, 'delete': h.sound.delete_sound}


class extension_feature(IsolatedAction):

    actions = {
        'generate': h.extension_feature.generate_extension_feature,
        'delete': h.extension_feature.delete_extension_feature,
    }


class iax(IsolatedAction):

    actions = {
        'generate': h.endpoint_iax.generate_iax,
        'delete': h.endpoint_iax.delete_iax,
    }


class skill(IsolatedAction):

    actions = {'generate': h.skill.generate_skill, 'delete': h.skill.delete_skill}


class skill_rule(IsolatedAction):

    actions = {
        'generate': h.skill_rule.generate_skill_rule,
        'delete': h.skill_rule.delete_skill_rule,
    }


class application(IsolatedAction):

    id_field = 'uuid'
    actions = {
        'generate': h.application.generate_application,
        'delete': h.application.delete_application,
    }


class access_feature(IsolatedAction):

    actions = {
        'generate': h.access_feature.generate_access_feature,
        'delete': h.access_feature.delete_access_feature,
    }


class transport(IsolatedAction):

    id_field = 'uuid'
    actions = {
        'generate': h.transport.generate_transport,
        'delete': h.transport.delete_transport,
    }
