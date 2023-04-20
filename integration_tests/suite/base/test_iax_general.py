# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from ..helpers import scenarios as s

from hamcrest import assert_that, has_entries
from . import confd
from ..helpers.config import TOKEN_SUB_TENANT


def test_put_errors():
    url = confd.asterisk.iax.general.put
    yield from error_checks(url)


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'ordered_options', 123
    yield s.check_bogus_field_returns_error, url, 'ordered_options', None
    yield s.check_bogus_field_returns_error, url, 'ordered_options', {}
    yield s.check_bogus_field_returns_error, url, 'ordered_options', 'string'
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [
        'string',
        'string',
    ]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [123, 123]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', ['string', 123]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [[]]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [{'key': 'value'}]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [['missing_value']]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [
        ['too', 'much', 'value']
    ]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [
        ['wrong_value', 1234]
    ]
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [
        ['none_value', None]
    ]

    yield s.check_bogus_field_returns_error, url, 'options', 123
    yield s.check_bogus_field_returns_error, url, 'options', None
    yield s.check_bogus_field_returns_error, url, 'options', 'string'
    yield s.check_bogus_field_returns_error, url, 'options', [['ordered', 'option']]
    yield s.check_bogus_field_returns_error, url, 'options', {'wrong_value': 23}
    yield s.check_bogus_field_returns_error, url, 'options', {'none_value': None}

    yield s.check_bogus_field_returns_error, url, 'options', {'register': 'value'}
    yield s.check_bogus_field_returns_error, url, 'ordered_options', [
        ['register', 'value']
    ]


def test_get():
    response = confd.asterisk.iax.general.get()
    response.assert_ok()


def test_edit_iax_general():
    parameters = {
        'ordered_options': [
            ['bindport', '5060'],
            ['allow', '127.0.0.1'],
            ['deny', '192.168.0.0'],
            ['allow', '192.168.0.1'],
        ],
        'options': {'nat': 'toto', 'username': 'Bob'},
    }

    response = confd.asterisk.iax.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.iax.general.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_iax_general_with_no_option():
    parameters = {'ordered_options': [], 'options': {}}
    response = confd.asterisk.iax.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.iax.general.get()
    assert_that(response.item, has_entries(parameters))


def test_edit_iax_general_with_none_value():
    parameters = {'ordered_options': [['bindport', 'ip']], 'options': {'nat': 'value'}}

    response = confd.asterisk.iax.general.put(**parameters)
    response.assert_updated()

    response = confd.asterisk.iax.general.get()
    assert_that(response.item, has_entries(parameters))


def test_restrict_only_master_tenant():
    response = confd.asterisk.iax.general.get(token=TOKEN_SUB_TENANT)
    response.assert_status(401)

    response = confd.asterisk.iax.general.put(token=TOKEN_SUB_TENANT)
    response.assert_status(401)


def test_bus_event_when_edited():
    url = confd.asterisk.iax.general
    headers = {}

    yield s.check_event, 'iax_general_edited', headers, url.put, {
        'ordered_options': [],
        'options': {},
    }
