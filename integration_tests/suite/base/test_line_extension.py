# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import assert_that, contains, contains_inanyorder, empty, has_entries

from ..helpers import scenarios as s, errors as e, associations as a, fixtures
from ..helpers.config import (
    EXTEN_OUTSIDE_RANGE,
    INCALL_CONTEXT,
    MAIN_TENANT,
    SUB_TENANT,
)
from . import confd, db

FAKE_ID = 999999999


@fixtures.line()
@fixtures.extension()
def test_associate_errors(line, extension):
    fake_line = confd.lines(FAKE_ID).extensions(extension['id']).put
    fake_extension = confd.lines(line['id']).extensions(FAKE_ID).put

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.extension(context='main-internal')
@fixtures.extension(context='sub-internal')
def test_associate_multi_tenant(main_ctx, sub_ctx, main_exten, sub_exten):
    @fixtures.line_sip(context=main_ctx, wazo_tenant=MAIN_TENANT)
    @fixtures.line_sip(context=sub_ctx, wazo_tenant=SUB_TENANT)
    def aux(main_line, sub_line):
        response = (
            confd.lines(sub_line['id'])
            .extensions(main_exten['id'])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Extension'))

        response = (
            confd.lines(main_line['id'])
            .extensions(sub_exten['id'])
            .put(wazo_tenant=SUB_TENANT)
        )
        response.assert_match(404, e.not_found('Line'))

        response = (
            confd.lines(main_line['id'])
            .extensions(sub_exten['id'])
            .put(wazo_tenant=MAIN_TENANT)
        )
        response.assert_match(400, e.different_tenant())

    aux()


@fixtures.line()
@fixtures.extension()
def test_dissociate_errors(line, extension):
    fake_line = confd.lines(FAKE_ID).extensions(extension['id']).delete
    fake_extension = confd.lines(line['id']).extensions(FAKE_ID).delete

    yield s.check_resource_not_found, fake_line, 'Line'
    yield s.check_resource_not_found, fake_extension, 'Extension'


@fixtures.context(wazo_tenant=MAIN_TENANT, name='main-internal')
@fixtures.context(wazo_tenant=SUB_TENANT, name='sub-internal')
@fixtures.extension(context='main-internal')
@fixtures.extension(context='sub-internal')
def test_dissociate_multi_tenant(main_ctx, sub_ctx, main_exten, sub_exten):
    @fixtures.line_sip(context=main_ctx, wazo_tenant=MAIN_TENANT)
    @fixtures.line_sip(context=sub_ctx, wazo_tenant=SUB_TENANT)
    def aux(main_line, sub_line):
        url = confd.lines(sub_line['id']).extensions(main_exten['id'])
        response = url.delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Extension'))

        url = confd.lines(main_line['id']).extensions(sub_exten['id'])
        response = url.delete(wazo_tenant=SUB_TENANT)
        response.assert_match(404, e.not_found('Line'))

    aux()


@fixtures.line_sip()
@fixtures.extension()
def test_associate_line_and_internal_extension(line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_updated()

    response = confd.lines(line['id']).get()
    assert_that(
        response.item['extensions'], contains(has_entries({'id': extension['id']}))
    )


@fixtures.extension(context=INCALL_CONTEXT)
@fixtures.line_sip()
def test_associate_extension_not_in_internal_context(extension, line):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.extension()
@fixtures.line_sip()
@fixtures.user()
@fixtures.user()
def test_associate_extension_to_one_line_multiple_users(
    extension, line, first_user, second_user
):
    with a.user_line(first_user, line), a.user_line(second_user, line):
        response = confd.lines(line['id']).extensions(extension['id']).put()
        response.assert_updated()


@fixtures.extension()
@fixtures.extension()
@fixtures.line_sip()
def test_associate_two_internal_extensions_to_same_line(
    first_extension, second_extension, line
):
    response = confd.lines(line['id']).extensions(first_extension['id']).put()
    response.assert_updated()

    response = confd.lines(line['id']).extensions(second_extension['id']).put()
    response.assert_match(400, e.resource_associated('Line', 'Extension'))


@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multi_lines_to_extension(extension, line1, line2, line3):
    response = confd.lines(line1['id']).extensions(extension['id']).put()
    response.assert_updated()

    response = confd.lines(line2['id']).extensions(extension['id']).put()
    response.assert_updated()

    response = confd.lines(line3['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.user()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multi_lines_to_extension_with_same_user(
    user, extension, line1, line2
):
    with a.user_line(user, line1), a.user_line(user, line2):
        response = confd.lines(line1['id']).extensions(extension['id']).put()
        response.assert_updated()

        response = confd.lines(line2['id']).extensions(extension['id']).put()
        response.assert_updated()


@fixtures.user()
@fixtures.user()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multi_lines_to_extension_with_different_user(
    user1, user2, exten, line1, line2
):
    with a.user_line(user1, line1), a.user_line(user2, line2):
        response = confd.lines(line1['id']).extensions(exten['id']).put()
        response.assert_updated()

        response = confd.lines(line2['id']).extensions(exten['id']).put()
        response.assert_match(400, e.resource_associated('User', 'Line'))


@fixtures.user()
@fixtures.extension()
@fixtures.extension()
@fixtures.line_sip()
@fixtures.line_sip()
def test_associate_multi_lines_to_multi_extensions_with_same_user(
    user, extension1, extension2, line1, line2
):
    with a.user_line(user, line1), a.user_line(user, line2):
        response = confd.lines(line1['id']).extensions(extension1['id']).put()
        response.assert_updated()

        response = confd.lines(line2['id']).extensions(extension2['id']).put()
        response.assert_updated()


@fixtures.extension()
@fixtures.line_sip()
def test_associate_line_to_extension_already_associated(extension, line):
    with a.line_extension(line, extension):
        response = confd.lines(line['id']).extensions(extension['id']).put()
        response.assert_updated()


@fixtures.line_sip()
def test_associate_line_to_extension_already_associated_to_other_resource(line):
    with db.queries() as queries:
        queries.insert_queue(number='1234', tenant_uuid=MAIN_TENANT)

    extension_id = confd.extensions.get(exten='1234').items[0]['id']

    response = confd.lines(line['id']).extensions(extension_id).put()
    response.assert_match(400, e.resource_associated('Extension', 'queue'))


@fixtures.line()
@fixtures.extension()
def test_associate_line_without_endpoint(line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_match(400, e.missing_association('Line', 'Endpoint'))


@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_associate_line_with_endpoint(line, sip, extension):
    with a.line_endpoint_sip(line, sip, check=False):
        response = confd.lines(line['id']).extensions(extension['id']).put()
        response.assert_updated()
        response = confd.lines(line['id']).get()
        assert_that(
            response.item['extensions'], contains(has_entries({'id': extension['id']})),
        )


@fixtures.line_sip()
@fixtures.extension(exten=EXTEN_OUTSIDE_RANGE)
def test_associate_when_exten_outside_range(line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_status(400)


@fixtures.line_sip()
@fixtures.extension(exten='_9123')
def test_associate_when_exten_pattern(line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).put()
    response.assert_updated()


@fixtures.line_sip()
@fixtures.extension()
def test_dissociate_line_and_extension(line, extension):
    with a.line_extension(line, extension, check=False):
        response = confd.lines(line['id']).extensions(extension['id']).delete()
        response.assert_deleted()


@fixtures.line_sip()
@fixtures.extension()
def test_dissociate_not_associated(line, extension):
    response = confd.lines(line['id']).extensions(extension['id']).delete()
    response.assert_deleted()


@fixtures.line_sip()
@fixtures.extension()
def test_delete_extension_associated_to_line(line, extension):
    with a.line_extension(line, extension):
        response = confd.extensions(extension['id']).delete()
        response.assert_match(400, e.resource_associated('Extension', 'Line'))


@fixtures.line_sip()
@fixtures.line_sip()
@fixtures.extension()
def test_get_multi_lines_extension(line1, line2, extension):
    with a.line_extension(line1, extension), a.line_extension(line2, extension):
        response = confd.extensions(extension['id']).get()
        assert_that(
            response.item,
            has_entries(
                lines=contains_inanyorder(
                    has_entries({'id': line1['id']}), has_entries({'id': line2['id']}),
                ),
            ),
        )


@fixtures.line_sip()
@fixtures.extension()
def test_dissociation(line, extension):
    with a.line_extension(line, extension, check=False):
        confd.lines(line['id']).extensions(extension['id']).delete().assert_deleted()
        response = confd.lines(line['id']).get()
        assert_that(response.item['extensions'], empty())


@fixtures.line_sip()
@fixtures.extension()
def test_edit_context_to_incall_when_associated(line, extension):
    with a.line_extension(line, extension, check=True):
        response = confd.extensions(extension['id']).put(context=INCALL_CONTEXT)
        response.assert_status(400)


@fixtures.line_sip()
@fixtures.extension()
def test_get_extension_relation(line, exten):
    with a.line_extension(line, exten):
        response = confd.lines(line['id']).get()
        assert_that(
            response.item['extensions'],
            contains(
                has_entries(
                    id=exten['id'], exten=exten['exten'], context=exten['context']
                )
            ),
        )


@fixtures.line()
@fixtures.sip()
@fixtures.extension()
def test_get_line_relation(line, sip, extension):
    with a.line_endpoint_sip(line, sip):
        with a.line_extension(line, extension):
            line = confd.lines(line['id']).get().item
            response = confd.extensions(extension['id']).get()
            assert_that(
                response.item['lines'],
                contains(has_entries(id=line['id'], name=line['name'])),
            )
