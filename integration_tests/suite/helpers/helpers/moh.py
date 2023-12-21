# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import string

from . import confd


def generate_moh(**parameters):
    parameters.setdefault('label', generate_name())
    parameters.setdefault('mode', 'files')
    return add_moh(**parameters)


def add_moh(wazo_tenant=None, **parameters):
    response = confd.moh.post(parameters, wazo_tenant=wazo_tenant)
    return response.item


def delete_moh(moh_uuid, check=False, **parameters):
    response = confd.moh(moh_uuid).delete()
    if check:
        response.assert_ok()


def generate_name():
    response = confd.moh.get()
    forbidden_names = {d['name'] for d in response.items}
    return _random_name(forbidden_names)


def _random_name(forbidden_names):
    name = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    if name in forbidden_names:
        return _random_name(forbidden_names)
    return name
