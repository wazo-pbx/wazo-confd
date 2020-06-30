# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from contextlib import contextmanager

from . import helpers as h


@contextmanager
def user_line(user, line, check=True):
    h.user_line.associate(user['id'], line['id'], check)
    yield
    h.user_line.dissociate(user['id'], line['id'], check)


@contextmanager
def user_voicemail(user, voicemail, check=True):
    h.user_voicemail.associate(user['id'], voicemail['id'], check)
    yield
    h.user_voicemail.dissociate(user['id'], voicemail['id'], check)


@contextmanager
def line_application(line, application, check=True):
    h.line_application.associate(line['id'], application['uuid'], check)
    yield
    h.line_application.dissociate(line['id'], application['uuid'], check)


@contextmanager
def line_extension(line, extension, check=True):
    h.line_extension.associate(line['id'], extension['id'], check)
    yield
    h.line_extension.dissociate(line['id'], extension['id'], check)


@contextmanager
def line_device(line, device, check=True):
    h.line_device.associate(line['id'], device['id'], check)
    yield
    h.line_device.dissociate(line['id'], device['id'], check)


@contextmanager
def line_endpoint_sip(line, sip, check=True):
    h.line_endpoint_sip.associate(line['id'], sip['uuid'], check)
    yield
    h.line_endpoint_sip.dissociate(line['id'], sip['uuid'], check)


@contextmanager
def line_endpoint_sccp(line, sccp, check=True):
    h.line_endpoint_sccp.associate(line['id'], sccp['id'], check)
    yield
    h.line_endpoint_sccp.dissociate(line['id'], sccp['id'], check)


@contextmanager
def line_endpoint_custom(line, custom, check=True):
    h.line_endpoint_custom.associate(line['id'], custom['id'], check)
    yield
    h.line_endpoint_custom.dissociate(line['id'], custom['id'], check)


@contextmanager
def user_call_permission(user, call_permission, check=True):
    h.user_call_permission.associate(user['id'], call_permission['id'], check)
    yield
    h.user_call_permission.dissociate(user['id'], call_permission['id'], check)


@contextmanager
def user_agent(user, agent, check=True):
    h.user_agent.associate(user['id'], agent['id'], check)
    yield
    h.user_agent.dissociate(user['id'], agent['id'], check)


@contextmanager
def user_funckey_template(user, funckey_template, check=True):
    h.user_funckey_template.associate(user['id'], funckey_template['id'], check)
    yield
    h.user_funckey_template.dissociate(user['id'], funckey_template['id'], check)


@contextmanager
def queue_extension(queue, extension, check=True):
    h.queue_extension.associate(queue['id'], extension['id'], check)
    yield
    h.queue_extension.dissociate(queue['id'], extension['id'], check)


@contextmanager
def trunk_endpoint_sip(trunk, sip, check=True):
    h.trunk_endpoint_sip.associate(trunk['id'], sip['uuid'], check)
    yield
    h.trunk_endpoint_sip.dissociate(trunk['id'], sip['uuid'], check)


@contextmanager
def trunk_endpoint_custom(trunk, custom, check=True):
    h.trunk_endpoint_custom.associate(trunk['id'], custom['id'], check)
    yield
    h.trunk_endpoint_custom.dissociate(trunk['id'], custom['id'], check)


@contextmanager
def trunk_endpoint_iax(trunk, iax, check=True):
    h.trunk_endpoint_iax.associate(trunk['id'], iax['id'], check)
    yield
    h.trunk_endpoint_iax.dissociate(trunk['id'], iax['id'], check)


@contextmanager
def incall_extension(incall, extension, check=True):
    h.incall_extension.associate(incall['id'], extension['id'], check)
    yield
    h.incall_extension.dissociate(incall['id'], extension['id'], check)


@contextmanager
def incall_user(incall, user, check=True):
    h.incall_user.associate(incall['id'], user['id'], check)
    yield
    h.incall_user.dissociate(incall['id'], user['id'], check)


@contextmanager
def outcall_trunk(outcall, *trunks, **kwargs):
    trunk_ids = [trunk['id'] for trunk in trunks]
    check = kwargs.get('check', True)
    h.outcall_trunk.associate(outcall['id'], trunk_ids, check=check)
    yield
    h.outcall_trunk.dissociate(outcall['id'], check=check)


@contextmanager
def outcall_extension(outcall, extension, **kwargs):
    h.outcall_extension.associate(outcall['id'], extension['id'], **kwargs)
    yield
    h.outcall_extension.dissociate(outcall['id'], extension['id'], **kwargs)


@contextmanager
def queue_member_agent(queue, agent, **kwargs):
    h.queue_member_agent.associate(queue['id'], agent['id'], **kwargs)
    yield
    h.queue_member_agent.dissociate(queue['id'], agent['id'], **kwargs)


@contextmanager
def queue_member_user(queue, user, **kwargs):
    h.queue_member_user.associate(queue['id'], user['id'], **kwargs)
    yield
    h.queue_member_user.dissociate(queue['id'], user['id'], **kwargs)


@contextmanager
def group_extension(group, extension, check=True):
    h.group_extension.associate(group['id'], extension['id'], check)
    yield
    h.group_extension.dissociate(group['id'], extension['id'], check)


@contextmanager
def group_member_extension(group, *extensions, **kwargs):
    check = kwargs.get('check', True)
    h.group_member_extension.associate(group['id'], extensions, check=check)
    yield
    h.group_member_extension.dissociate(group['id'], check=check)


@contextmanager
def group_member_user(group, *users, **kwargs):
    user_uuids = [user['uuid'] for user in users]
    check = kwargs.get('check', True)
    h.group_member_user.associate(group['id'], user_uuids, check=check)
    yield
    h.group_member_user.dissociate(group['id'], check=check)


@contextmanager
def conference_extension(conference, extension, check=True):
    h.conference_extension.associate(conference['id'], extension['id'], check)
    yield
    h.conference_extension.dissociate(conference['id'], extension['id'], check)


@contextmanager
def parking_lot_extension(parking_lot, extension, check=True):
    h.parking_lot_extension.associate(parking_lot['id'], extension['id'], check)
    yield
    h.parking_lot_extension.dissociate(parking_lot['id'], extension['id'], check)


@contextmanager
def paging_member_user(paging, *users, **kwargs):
    user_uuids = [user['uuid'] for user in users]
    check = kwargs.get('check', True)
    h.paging_member_user.associate(paging['id'], user_uuids, check=check)
    yield
    h.paging_member_user.dissociate(paging['id'], check=check)


@contextmanager
def paging_caller_user(paging, *users, **kwargs):
    user_uuids = [user['uuid'] for user in users]
    check = kwargs.get('check', True)
    h.paging_caller_user.associate(paging['id'], user_uuids, check=check)
    yield
    h.paging_caller_user.dissociate(paging['id'], check=check)


@contextmanager
def switchboard_member_user(switchboard, users, check=True):
    user_uuids = [user['uuid'] for user in users]
    h.switchboard_member_user.associate(switchboard['uuid'], user_uuids, check=check)
    yield
    h.switchboard_member_user.dissociate(switchboard['uuid'], check=check)


@contextmanager
def incall_schedule(incall, schedule, check=True):
    h.incall_schedule.associate(incall['id'], schedule['id'], check)
    yield
    h.incall_schedule.dissociate(incall['id'], schedule['id'], check)


@contextmanager
def user_schedule(user, schedule, check=True):
    h.user_schedule.associate(user['uuid'], schedule['id'], check)
    yield
    h.user_schedule.dissociate(user['uuid'], schedule['id'], check)


@contextmanager
def group_schedule(group, schedule, check=True):
    h.group_schedule.associate(group['id'], schedule['id'], check)
    yield
    h.group_schedule.dissociate(group['id'], schedule['id'], check)


@contextmanager
def queue_schedule(queue, schedule, check=True):
    h.queue_schedule.associate(queue['id'], schedule['id'], check)
    yield
    h.queue_schedule.dissociate(queue['id'], schedule['id'], check)


@contextmanager
def outcall_schedule(outcall, schedule, check=True):
    h.outcall_schedule.associate(outcall['id'], schedule['id'], check)
    yield
    h.outcall_schedule.dissociate(outcall['id'], schedule['id'], check)


@contextmanager
def outcall_call_permission(outcall, call_permission, check=True):
    h.outcall_call_permission.associate(outcall['id'], call_permission['id'], check)
    yield
    h.outcall_call_permission.dissociate(outcall['id'], call_permission['id'], check)


@contextmanager
def group_call_permission(group, call_permission, check=True):
    h.group_call_permission.associate(group['id'], call_permission['id'], check)
    yield
    h.group_call_permission.dissociate(group['id'], call_permission['id'], check)


@contextmanager
def trunk_register_iax(trunk, iax, check=True):
    h.trunk_register_iax.associate(trunk['id'], iax['id'], check)
    yield
    h.trunk_register_iax.dissociate(trunk['id'], iax['id'], check)


@contextmanager
def call_filter_recipient_user(call_filter, *users, **kwargs):
    user_uuids = [user['uuid'] for user in users]
    check = kwargs.get('check', True)
    h.call_filter_recipient_user.associate(call_filter['id'], user_uuids, check=check)
    yield
    h.call_filter_recipient_user.dissociate(call_filter['id'], check=check)


@contextmanager
def call_filter_surrogate_user(call_filter, *users, **kwargs):
    user_uuids = [user['uuid'] for user in users]
    check = kwargs.get('check', True)
    h.call_filter_surrogate_user.associate(call_filter['id'], user_uuids, check=check)
    yield
    h.call_filter_surrogate_user.dissociate(call_filter['id'], check=check)


@contextmanager
def call_pickup_interceptor_user(call_pickup, *users, **kwargs):
    user_uuids = [user['uuid'] for user in users]
    check = kwargs.get('check', True)
    h.call_pickup_interceptor_user.associate(call_pickup['id'], user_uuids, check=check)
    yield
    h.call_pickup_interceptor_user.dissociate(call_pickup['id'], check=check)


@contextmanager
def call_pickup_target_user(call_pickup, *users, **kwargs):
    user_uuids = [user['uuid'] for user in users]
    check = kwargs.get('check', True)
    h.call_pickup_target_user.associate(call_pickup['id'], user_uuids, check=check)
    yield
    h.call_pickup_target_user.dissociate(call_pickup['id'], check=check)


@contextmanager
def call_pickup_interceptor_group(call_pickup, *groups, **kwargs):
    group_ids = [group['id'] for group in groups]
    check = kwargs.get('check', True)
    h.call_pickup_interceptor_group.associate(call_pickup['id'], group_ids, check=check)
    yield
    h.call_pickup_interceptor_group.dissociate(call_pickup['id'], check=check)


@contextmanager
def call_pickup_target_group(call_pickup, *groups, **kwargs):
    group_ids = [group['id'] for group in groups]
    check = kwargs.get('check', True)
    h.call_pickup_target_group.associate(call_pickup['id'], group_ids, check=check)
    yield
    h.call_pickup_target_group.dissociate(call_pickup['id'], check=check)


@contextmanager
def context_context(context, *contexts, **kwargs):
    context_ids = [c['id'] for c in contexts]
    check = kwargs.get('check', True)
    h.context_context.associate(context['id'], context_ids, check=check)
    yield
    h.context_context.dissociate(context['id'], check=check)


@contextmanager
def agent_skill(agent, skill, **kwargs):
    h.agent_skill.associate(agent['id'], skill['id'], **kwargs)
    yield
    h.agent_skill.dissociate(agent['id'], skill['id'], **kwargs)


@contextmanager
def transport_endpoint_sip(transport, sip, check=True):
    h.transport_endpoint_sip.associate(transport['uuid'], sip['uuid'], check)
    yield
    h.transport_endpoint_sip.dissociate(transport['uuid'], sip['uuid'], check)
