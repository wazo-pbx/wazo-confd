# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from . import confd


def associate(group_id, schedule_id, check=True):
    response = confd.groups(group_id).schedules(schedule_id).put()
    if check:
        response.assert_ok()


def dissociate(group_id, schedule_id, check=True):
    response = confd.groups(group_id).schedules(schedule_id).delete()
    if check:
        response.assert_ok()
