# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from base64 import b64encode
from hamcrest import (
    all_of,
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    has_entries,
    has_entry,
    has_item,
    has_items,
    has_properties,
    is_not,
    not_,
    not_none,
)
from datetime import datetime, timedelta

from . import (
    BaseIntegrationTest,
    confd,
    create_confd,
    db,
)
from ..helpers import (
    bus,
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import MAIN_TENANT, SUB_TENANT

FAKE_UUID = '99999999-9999-4999-9999-999999999999'


@fixtures.user()
def test_get_errors(me):
    fake_get = confd.meetings(FAKE_UUID).get
    yield s.check_resource_not_found, fake_get, 'Meeting'

    user_confd = create_confd(user_uuid=me['uuid'])
    fake_get = user_confd.users.me.meetings(FAKE_UUID).get
    yield s.check_resource_not_found, fake_get, 'Meeting'


@fixtures.user()
def test_post_errors(me):
    url = confd.meetings.post
    for check in error_checks(url):
        yield check

    user_confd = create_confd(user_uuid=me['uuid'])
    url = user_confd.users.me.meetings.post
    for check in error_checks(url):
        yield check


@fixtures.ingress_http()
@fixtures.meeting()
def test_put_errors(_, meeting):
    url = confd.meetings(meeting['uuid']).put
    for check in error_checks(url):
        yield check


@fixtures.ingress_http()
@fixtures.user()
def test_put_errors_users_me(_, me):
    user_confd = create_confd(user_uuid=me['uuid'])
    with fixtures.user_me_meeting(user_confd) as meeting:
        url = user_confd.users.me.meetings(meeting['uuid']).put
        for check in error_checks(url):
            yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', 123
    yield s.check_bogus_field_returns_error, url, 'name', None
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', 'a' * 513
    yield s.check_bogus_field_returns_error, url, 'persistent', None
    yield s.check_bogus_field_returns_error, url, 'persistent', 42
    yield s.check_bogus_field_returns_error, url, 'persistent', 'no'
    yield s.check_bogus_field_returns_error, url, 'persistent', []
    yield s.check_bogus_field_returns_error, url, 'persistent', {}


@fixtures.ingress_http(wazo_tenant=MAIN_TENANT)
@fixtures.ingress_http(wazo_tenant=SUB_TENANT)
@fixtures.meeting(wazo_tenant=MAIN_TENANT)
@fixtures.meeting(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(_, __, main, sub):
    response = confd.meetings.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.meetings.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.meetings.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.ingress_http()
@fixtures.user()
@fixtures.meeting(name='ignored')
def test_list_user_me(_, me, __):
    user_confd = create_confd(user_uuid=me['uuid'])
    with fixtures.user_me_meeting(user_confd) as mine_1, fixtures.user_me_meeting(
        user_confd
    ) as mine_2:
        response = user_confd.users.me.meetings.get()
        assert_that(
            response,
            has_properties(
                total=equal_to(2),
                items=contains_inanyorder(mine_1, mine_2),
            ),
        )


@fixtures.ingress_http()
@fixtures.meeting(name="search", persistent=True)
@fixtures.meeting(name="hidden", persistent=False)
def test_search(_, meeting, hidden):
    url = confd.meetings
    searches = {'name': 'search'}

    for field, term in searches.items():
        yield check_search, url, meeting, hidden, field, term

    response = url.get(persistent=True)
    assert_that(response.items, has_item(meeting))
    assert_that(response.items, is_not(has_item(hidden)))

    response = url.get(persistent=False)
    assert_that(response.items, has_item(hidden))
    assert_that(response.items, is_not(has_item(meeting)))


def check_search(url, meeting, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, meeting[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: meeting[field]})

    assert_that(response.items, has_item(has_entry('uuid', meeting['uuid'])))
    assert_that(response.items, is_not(has_item(has_entry('uuid', hidden['uuid']))))


@fixtures.ingress_http()
@fixtures.meeting(name="sort1")
@fixtures.meeting(name="sort2")
def test_sorting_offset_limit(_, meeting1, meeting2):
    url = confd.meetings.get
    yield s.check_sorting, url, meeting1, meeting2, 'name', 'sort', 'uuid'

    yield s.check_offset, url, meeting1, meeting2, 'name', 'sort', 'uuid'
    yield s.check_limit, url, meeting1, meeting2, 'name', 'sort', 'uuid'


@fixtures.ingress_http()
@fixtures.user()
@fixtures.meeting()
def test_get(_, me, other_meeting):
    user_confd = create_confd(user_uuid=me['uuid'])
    with fixtures.user_me_meeting(user_confd) as mine:
        response = confd.meetings(other_meeting['uuid']).get()
        assert_that(response.item, has_entries(uuid=other_meeting['uuid']))

        response = confd.guests.me.meetings(other_meeting['uuid']).get()
        assert_that(response.item, has_entries(uuid=other_meeting['uuid']))

        response = user_confd.users.me.meetings(other_meeting['uuid']).get()
        assert_that(response.item, has_entries(uuid=other_meeting['uuid']))

        response = user_confd.users.me.meetings(mine['uuid']).get()
        assert_that(response.item, has_entries(name=mine['name']))


@fixtures.ingress_http(wazo_tenant=MAIN_TENANT)
@fixtures.ingress_http(wazo_tenant=SUB_TENANT)
@fixtures.meeting(wazo_tenant=MAIN_TENANT)
@fixtures.meeting(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(_, __, main, sub):
    response = confd.meetings(main['uuid']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Meeting'))

    response = confd.meetings(sub['uuid']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_no_ingress_http_configured():
    response = confd.meetings.post(name='error')
    assert_that(
        response,
        has_properties(
            status=503,
            json=contains('no Ingress HTTP configured'),
        ),
    )


@fixtures.ingress_http()
@fixtures.user()
def test_create_minimal_parameters(ingress_http, me):
    response = confd.meetings.post(name='minimal')
    response.assert_created('meetings')

    assert_that(
        response.item,
        has_entries(
            tenant_uuid=MAIN_TENANT,
            uuid=not_(empty()),
            name='minimal',
            ingress_http_uri=ingress_http['uri'],
            persistent=False,
        ),
    )

    confd.meetings(response.item['uuid']).delete().assert_deleted()

    user_confd = create_confd(user_uuid=me['uuid'])
    response = user_confd.users.me.meetings.post(name='minimal')
    response.assert_created('meetings')

    assert_that(
        response.item,
        has_entries(
            tenant_uuid=MAIN_TENANT,
            uuid=not_(empty()),
            owner_uuids=contains_inanyorder(me['uuid']),
            name='minimal',
            ingress_http_uri=ingress_http['uri'],
            persistent=False,
        ),
    )

    confd.meetings(response.item['uuid']).delete().assert_deleted()


@fixtures.ingress_http(uri='https://wazo.example.com:10443')
@fixtures.user()
@fixtures.user()
def test_create_all_parameters(ingress_http, me, owner):
    parameters = {
        'name': 'allparameter',
        'owner_uuids': [owner['uuid']],
        'persistent': True,
    }

    response = confd.meetings.post(**parameters)
    response.assert_created('meetings')
    assert_that(
        response.item,
        has_entries(
            name=parameters['name'],
            tenant_uuid=MAIN_TENANT,
            owner_uuids=contains_inanyorder(owner['uuid']),
            ingress_http_uri=ingress_http['uri'],
            persistent=True,
        ),
    )
    confd.meetings(response.item['uuid']).delete().assert_deleted()

    user_confd = create_confd(user_uuid=me['uuid'])
    response = user_confd.users.me.meetings.post(**parameters)
    response.assert_created('meetings')
    assert_that(
        response.item,
        has_entries(
            name=parameters['name'],
            tenant_uuid=MAIN_TENANT,
            ingress_http_uri=ingress_http['uri'],
            owner_uuids=contains_inanyorder(me['uuid'], owner['uuid']),
            persistent=True,
        ),
    )
    confd.meetings(response.item['uuid']).delete().assert_deleted()


@fixtures.ingress_http()
@fixtures.sip_template()
def test_guest_endpoint_sip_creation(_, template):
    with db.queries() as queries:
        queries.set_tenant_templates(
            MAIN_TENANT, meeting_guest_sip_template_uuid=template['uuid']
        )

    response = confd.meetings.post({'name': 'testing'})
    meeting = response.item

    endpoint_sip_name = 'wazo-meeting-{uuid}-guest'.format(**meeting)
    response = confd.endpoints.sip.get(name=endpoint_sip_name)
    assert_that(response.total, equal_to(1))

    endpoint_sip = response.items[0]
    endpoint_username = None
    endpoint_password = None
    endpoint_context = None

    for option, value in endpoint_sip['auth_section_options']:
        if option == 'username':
            endpoint_username = value
        elif option == 'password':
            endpoint_password = value

    for option, value in endpoint_sip['endpoint_section_options']:
        if option == 'context':
            endpoint_context = value

    assert_that(endpoint_username, not_none())
    assert_that(endpoint_password, not_none())
    assert_that(endpoint_context, equal_to('wazo-meeting-guest'))

    guest_sip_authorization = b64encode(
        '{}:{}'.format(endpoint_username, endpoint_password).encode()
    ).decode()
    assert_that(
        meeting,
        has_entries(
            guest_sip_authorization=guest_sip_authorization,
        ),
    )

    response = confd.meetings(meeting['uuid']).delete()
    response.assert_deleted()

    response = confd.endpoints.sip(endpoint_sip['uuid']).get()
    response.assert_status(404)


@fixtures.ingress_http()
def test_create_without_name(_):
    response = confd.meetings.post()
    response.assert_status(400)


@fixtures.ingress_http()
@fixtures.meeting()
def test_edit_minimal_parameters(_, meeting):
    response = confd.meetings(meeting['uuid']).put()
    response.assert_updated()


@fixtures.ingress_http()
@fixtures.meeting()
@fixtures.user()
def test_edit_all_parameters(_, meeting, some_user):
    parameters = {
        'name': 'editallparameter',
        'owner_uuids': [some_user['uuid']],
    }
    response = confd.meetings(meeting['uuid']).put(**parameters)
    response.assert_updated()

    response = confd.meetings(meeting['uuid']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.ingress_http()
@fixtures.user()
@fixtures.user()
@fixtures.meeting()
def test_edit_all_parameters_users_me(_, me, other_user, other_meeting):
    user_confd = create_confd(user_uuid=me['uuid'])
    with fixtures.user_me_meeting(user_confd) as mine:
        parameters = {
            'name': 'editallparameter',
            'owner_uuids': [other_user['uuid']],
        }
        expected_parameters = {
            'name': 'editallparameter',
            'owner_uuids': [me['uuid'], other_user['uuid']],
        }

        response = user_confd.users.me.meetings(mine['uuid']).put(**parameters)
        response.assert_updated()

        response = user_confd.users.me.meetings(mine['uuid']).get()
        assert_that(response.item, has_entries(expected_parameters))

        response = user_confd.users.me.meetings(other_meeting['uuid']).put(**parameters)
        response.assert_match(404, e.not_found(resource='Meeting'))


@fixtures.ingress_http(wazo_tenant=MAIN_TENANT)
@fixtures.ingress_http(wazo_tenant=SUB_TENANT)
@fixtures.meeting(wazo_tenant=MAIN_TENANT)
@fixtures.meeting(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(_, __, main, sub):
    response = confd.meetings(main['uuid']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Meeting'))

    response = confd.meetings(sub['uuid']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.ingress_http()
@fixtures.meeting()
def test_delete(_, meeting):
    response = confd.meetings(meeting['uuid']).delete()
    response.assert_deleted()
    confd.meetings(meeting['uuid']).get().assert_status(404)


@fixtures.ingress_http()
@fixtures.user()
@fixtures.meeting()
def test_delete_users_me(_, me, other_meeting):
    user_confd = create_confd(user_uuid=me['uuid'])
    with fixtures.user_me_meeting(user_confd) as mine:
        response = user_confd.users.me.meetings(mine['uuid']).delete()
        response.assert_deleted()
        confd.meetings(mine['uuid']).get().assert_status(404)

        response = user_confd.users.me.meetings(other_meeting['uuid']).delete()
        response.assert_match(404, e.not_found(resource='Meeting'))


@fixtures.ingress_http(wazo_tenant=MAIN_TENANT)
@fixtures.ingress_http(wazo_tenant=SUB_TENANT)
@fixtures.meeting(wazo_tenant=MAIN_TENANT)
@fixtures.meeting(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(_, __, main, sub):
    response = confd.meetings(main['uuid']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Meeting'))

    response = confd.meetings(sub['uuid']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.ingress_http()
@fixtures.meeting()
def test_bus_events(_, meeting):
    yield s.check_bus_event, 'config.meetings.created', confd.meetings.post, {
        'name': 'meeting'
    }
    yield s.check_bus_event, 'config.meetings.updated', confd.meetings(
        meeting['uuid']
    ).put
    yield s.check_bus_event, 'config.meetings.deleted', confd.meetings(
        meeting['uuid']
    ).delete


@fixtures.ingress_http()
@fixtures.user()
@fixtures.meeting()
def test_bus_events_progress(_, me, meeting):
    yield s.check_bus_event, 'config.meetings.progress', bus.BusClientHeaders.send_meeting_reload_complete_event, meeting

    my_uuid = me['uuid']
    user_confd = create_confd(user_uuid=my_uuid)
    with fixtures.user_me_meeting(user_confd) as mine:
        yield s.check_bus_event, f'config.users.{my_uuid}.meetings.progress', bus.BusClientHeaders.send_meeting_reload_complete_event, mine


@fixtures.ingress_http()
@fixtures.meeting()
@fixtures.meeting()
def test_purge_old_meetings(_, meeting_too_old, meeting_too_young):
    too_old = datetime.now() - timedelta(hours=72)
    with db.queries() as queries:
        queries.set_meeting_creation_date(meeting_too_old['uuid'], too_old)

    BaseIntegrationTest.purge_meetings()

    response = confd.meetings(meeting_too_old['uuid']).get()
    response.assert_status(404)
    response = confd.meetings(meeting_too_young['uuid']).get()
    response.assert_status(200)
