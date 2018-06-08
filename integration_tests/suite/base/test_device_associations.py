# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from hamcrest import assert_that, has_entries


from ..helpers import config
from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import associations as a
from ..helpers import helpers as h
from . import mocks, provd, db, confd


@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
@fixtures.device()
def test_when_extension_updated_on_sip_line_then_provd_is_updated(user, line, sip, extension, device):
    exten = h.extension.find_available_exten(config.CONTEXT)
    line_cid = h.extension.find_available_exten(config.CONTEXT, exclude=[exten])

    with a.line_endpoint_sip(line, sip), a.user_line(user, line), \
            a.line_extension(line, extension), a.line_device(line, device):

        response = confd.extensions(extension['id']).put(exten=exten)
        response.assert_updated()

        response = confd.lines(line['id']).put(caller_id_num=line_cid)
        response.assert_updated()

        provd_config = provd.configs.get(device['id'])
        sip_line = provd_config['raw_config']['sip_lines']['1']
        assert_that(sip_line, has_entries(number=exten))


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
@fixtures.device()
def test_when_caller_id_updated_on_line_then_provd_is_updated(user, line, extension, device):
    with a.user_line(user, line), a.line_extension(line, extension), a.line_device(line, device):
        response = confd.lines(line['id']).put(caller_id_name="jôhn smîth", caller_id_num="1000")
        response.assert_updated()

        provd_config = provd.configs.get(device['id'])
        sip_line = provd_config['raw_config']['sip_lines']['1']
        assert_that(sip_line, has_entries({'display_name': 'jôhn smîth',
                                           'number': extension['exten']}))


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
@fixtures.device()
def test_when_caller_id_updated_on_user_then_provd_is_updated(user, line, extension, device):
    with a.user_line(user, line), a.line_extension(line, extension), a.line_device(line, device):
        response = confd.users(user['id']).put(caller_id='"rôger rabbit" <1000>')
        response.assert_updated()

        provd_config = provd.configs.get(device['id'])
        sip_line = provd_config['raw_config']['sip_lines']['1']
        assert_that(sip_line, has_entries({'display_name': 'rôger rabbit',
                                           'number': extension['exten']}))


@mocks.provd()
@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
@fixtures.device()
def test_when_sip_username_and_password_are_updated_then_provd_is_updated(provd, user, line, sip, extension, device):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line), \
            a.line_extension(line, extension), a.line_device(line, device):

        response = confd.endpoints.sip(sip['id']).put(username="myusername",
                                                      secret="mysecret")
        response.assert_updated()

        provd_config = provd.configs.get(device['id'])
        sip_line = provd_config['raw_config']['sip_lines']['1']
        assert_that(sip_line, has_entries({'auth_username': 'myusername',
                                           'username': 'myusername',
                                           'password': 'mysecret'}))


@mocks.provd()
@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
@fixtures.device()
def test_given_config_registrar_has_changed_when_sip_line_updated_then_provd_updated(provd, user, line, sip, extension, device):
    registrar = provd.configs.get('default')
    registrar['registrar_main'] = '10.0.1.2'
    registrar['proxy_main'] = '11.1.2.3'
    provd.configs.update(registrar)

    with a.line_endpoint_sip(line, sip), a.user_line(user, line), \
            a.line_extension(line, extension), a.line_device(line, device):

        response = confd.lines(line['id']).put()
        response.assert_updated()

        provd_config = provd.configs.get(device['id'])
        sip_line = provd_config['raw_config']['sip_lines']['1']
        assert_that(sip_line, has_entries(registrar_ip='10.0.1.2',
                                          proxy_ip='11.1.2.3'))


@mocks.provd()
@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
@fixtures.device()
def test_given_backup_registrar_has_changed_when_sip_line_updated_then_provd_updated(provd, user, line, sip, extension, device):
    registrar = provd.configs.get('default')
    registrar['registrar_backup'] = '20.1.2.3'
    registrar['proxy_backup'] = '20.2.3.4'
    provd.configs.update(registrar)

    with a.line_endpoint_sip(line, sip), a.user_line(user, line), \
            a.line_extension(line, extension), a.line_device(line, device):

        response = confd.lines(line['id']).put()
        response.assert_updated()

        provd_config = provd.configs.get(device['id'])
        sip_line = provd_config['raw_config']['sip_lines']['1']
        assert_that(sip_line, has_entries(backup_registrar_ip='20.1.2.3',
                                          backup_proxy_ip='20.2.3.4'))


@mocks.provd()
@fixtures.user()
@fixtures.line()
@fixtures.sccp()
@fixtures.extension()
@fixtures.device()
def test_given_backup_registrar_has_changed_when_sccp_line_updated_then_provd_updated(provd, user, line, sccp, extension, device):
    registrar = provd.configs.get('default')
    registrar['proxy_backup'] = '20.2.3.4'
    provd.configs.update(registrar)

    with a.line_endpoint_sccp(line, sccp), a.user_line(user, line), \
            a.line_extension(line, extension), a.line_device(line, device):

        response = confd.lines(line['id']).put()
        response.assert_updated()

        provd_config = provd.configs.get(device['id'])
        sccp_config = provd_config['raw_config']['sccp_call_managers']['2']
        assert_that(sccp_config, has_entries(ip='20.2.3.4'))


@fixtures.line()
@fixtures.sip()
@fixtures.autoprov()
def test_updating_line_associated_with_autoprov_device_does_not_fail(line, sip, device):
    with a.line_endpoint_sip(line, sip, check=False):
        with db.queries() as queries:
            queries.associate_line_device(line['id'], device['id'])
        response = confd.lines(line['id']).put()
        response.assert_ok()


@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
@fixtures.autoprov()
def test_updating_user_line_or_extension_associated_with_autoprov_device_does_not_fail(user, line, sip, extension, device):
    with a.line_endpoint_sip(line, sip, check=False), a.line_extension(line, extension, check=False), \
            a.user_line(user, line, check=False):

        with db.queries() as queries:
            queries.associate_line_device(line['id'], device['id'])

        response = confd.endpoints.sip(sip['id']).put()
        response.assert_ok()

        response = confd.lines(line['id']).put()
        response.assert_ok()

        response = confd.users(user['id']).put()
        response.assert_ok()

        response = confd.extensions(extension['id']).put()
        response.assert_ok()


@fixtures.user()
@fixtures.line()
@fixtures.sccp()
@fixtures.extension()
def test_given_extension_associated_to_sccp_line_when_updated_then_cid_num_updated(user, line, sccp, extension):
    exten = h.extension.find_available_exten(config.CONTEXT)

    with a.line_endpoint_sccp(line, sccp), a.line_extension(line, extension), a.user_line(user, line):
        confd.extensions(extension['id']).put(exten=exten).assert_updated()

        response = confd.lines(line['id']).get()
        assert_that(response.item, has_entries(caller_id_num=exten))


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
@fixtures.device()
def test_dissociate_line_associated_to_a_device(user, line, extension, device):
    with a.line_extension(line, extension), a.user_line(user, line), a.line_device(line, device):
        response = confd.lines(line['id']).extensions(extension['id']).delete()
        response.assert_match(400, e.resource_associated('Line', 'Device'))


@fixtures.user()
@fixtures.line_sip()
@fixtures.extension()
@fixtures.device()
def test_dissociate_user_line_when_device_is_associated(user, line, extension, device):
    with a.user_line(user, line), a.line_extension(line, extension), a.line_device(line, device):
        response = confd.users(user['id']).lines(line['id']).delete()
        response.assert_match(400, e.resource_associated('Line', 'Device'))


@fixtures.user()
@fixtures.line()
@fixtures.sip()
@fixtures.extension()
@fixtures.device()
def test_dissociate_sip_endpoint_associated_to_device(user, line, sip, extension, device):
    with a.line_endpoint_sip(line, sip), a.user_line(user, line), a.line_extension(line, extension), a.line_device(line, device):
        response = confd.lines(line['id']).endpoints.sip(sip['id']).delete()
        response.assert_match(400, e.resource_associated())


@fixtures.user()
@fixtures.line()
@fixtures.extension()
@fixtures.sccp()
@fixtures.device()
def test_dissociate_sccp_endpoint_associated_to_device(user, line, extension, sccp, device):
    with a.line_endpoint_sccp(line, sccp), a.user_line(user, line), a.line_extension(line, extension), a.line_device(line, device):
        response = confd.lines(line['id']).endpoints.sccp(sccp['id']).delete()
        response.assert_match(400, e.resource_associated())
