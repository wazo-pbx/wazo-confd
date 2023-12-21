# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, has_entries

from ..helpers import scenarios as s
from ..helpers.config import TOKEN_SUB_TENANT
from . import confd


def test_put_errors():
    url = confd.asterisk.pjsip.global_.put
    yield from error_checks(url)


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'options', 123
    yield s.check_bogus_field_returns_error, url, 'options', None
    yield s.check_bogus_field_returns_error, url, 'options', 'string'
    yield s.check_bogus_field_returns_error, url, 'options', [['ordered', 'option']]
    yield s.check_bogus_field_returns_error, url, 'options', {'wrong_value': 23}
    yield s.check_bogus_field_returns_error, url, 'options', {'none_value': None}
    # Not a global option
    yield s.check_bogus_field_returns_error, url, 'options', {'compact_headers': 'yes'}
    # Type is an internal field
    yield s.check_bogus_field_returns_error, url, 'options', {'type': 'endpoint'}


def test_get():
    response = confd.asterisk.pjsip.global_.get()
    response.assert_ok()


def test_edit():
    parameters = {'options': {'max_forwards': '5', 'keep_alive_interval': '30'}}

    response = confd.asterisk.pjsip.global_.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.pjsip.global_.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_with_no_option():
    parameters = {'options': {}}
    response = confd.asterisk.pjsip.global_.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.pjsip.global_.get()
    assert_that(response.item, has_entries(parameters))


def test_restrict_only_master_tenant():
    response = confd.asterisk.pjsip.global_.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.asterisk.pjsip.global_.put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)


def test_bus_event_when_edited():
    url = confd.asterisk.pjsip.global_
    headers = {}

    yield s.check_event, 'pjsip_global_updated', headers, url.put, {'options': {}}
