# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    contains,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    not_,
)

from . import confd
from ..helpers import errors as e, fixtures, scenarios as s
from ..helpers.config import MAIN_TENANT, SUB_TENANT
from ..helpers.helpers.destination import invalid_destinations, valid_destinations


def test_get_errors():
    fake_schedule = confd.schedules(999999).get
    yield s.check_resource_not_found, fake_schedule, 'Schedule'


def test_delete_errors():
    fake_schedule = confd.schedules(999999).delete
    yield s.check_resource_not_found, fake_schedule, 'Schedule'


@fixtures.user()
def test_post_errors(user):
    url = confd.schedules.post
    yield from error_checks(url, user)


@fixtures.schedule()
@fixtures.user()
def test_put_errors(schedule, user):
    url = confd.schedules(schedule['id']).put
    yield from error_checks(url, user)


def error_checks(url, user):
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', 1234
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}
    yield s.check_bogus_field_returns_error, url, 'timezone', True
    yield s.check_bogus_field_returns_error, url, 'timezone', 1234
    yield s.check_bogus_field_returns_error, url, 'timezone', s.random_string(129)
    yield s.check_bogus_field_returns_error, url, 'timezone', []
    yield s.check_bogus_field_returns_error, url, 'timezone', {}
    yield s.check_bogus_field_returns_error, url, 'enabled', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'enabled', None
    yield s.check_bogus_field_returns_error, url, 'enabled', []
    yield s.check_bogus_field_returns_error, url, 'enabled', {}
    yield s.check_bogus_field_returns_error, url, 'open_periods', True
    yield s.check_bogus_field_returns_error, url, 'open_periods', 1234
    yield s.check_bogus_field_returns_error, url, 'open_periods', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'open_periods', {}
    yield s.check_bogus_field_returns_error, url, 'exceptional_periods', True
    yield s.check_bogus_field_returns_error, url, 'exceptional_periods', None
    yield s.check_bogus_field_returns_error, url, 'exceptional_periods', 1234
    yield s.check_bogus_field_returns_error, url, 'exceptional_periods', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'exceptional_periods', {}

    for key in ('open_periods', 'exceptional_periods'):
        regex = fr'{key}.*0.*hours_start'
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'hours_start': 7}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'hours_start': '7:15'}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'hours_start': 'abcd'}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'hours_start': None}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'hours_start': '24:00'}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'hours_start': '10:60'}
        ], regex

        regex = fr'{key}.*0.*hours_end'
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'hours_end': 8}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'hours_end': '8:15'}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'hours_end': 'abcd'}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'hours_end': None}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'hours_end': '24:00'}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'hours_end': '10:60'}
        ], regex

        regex = fr'{key}.*0.*week_days'
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'week_days': None}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'week_days': 1}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'week_days': []}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'week_days': ['1-2']}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'week_days': [None]}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'week_days': [-1]}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'week_days': [8]}
        ], regex

        regex = fr'{key}.*0.*month_days'
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'month_days': None}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'month_days': 1}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'month_days': []}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'month_days': ['1-2']}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'month_days': [None]}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'month_days': [-1]}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'month_days': [32]}
        ], regex

        regex = fr'{key}.*0.*months'
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'months': None}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'months': 1}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'months': []}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'months': ['1-2']}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'months': [None]}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'months': [-1]}
        ], regex
        yield s.check_bogus_field_returns_error_matching_regex, url, key, [
            {'months': [13]}
        ], regex

    for destination in invalid_destinations():
        yield s.check_bogus_field_returns_error, url, 'closed_destination', destination
    yield s.check_bogus_field_returns_error, url, 'closed_destination', {
        'type': 'user',
        'user_id': user['id'],
        'moh_uuid': '00000000-0000-0000-0000-000000000000',
    }, {}, 'MOH was not found'

    for destination in invalid_destinations():
        regex = r'exceptional_periods.*0.*destination'
        body = [{'destination': destination}]
        yield s.check_bogus_field_returns_error_matching_regex, url, 'exceptional_periods', body, regex


@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.schedules.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.schedules.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.schedules.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.schedule(name='search', timezone='search')
@fixtures.schedule(name='hidden', timezone='hidden')
def test_search(schedule, hidden):
    url = confd.schedules
    searches = {'name': 'search', 'timezone': 'search'}

    for field, term in searches.items():
        yield check_search, url, schedule, hidden, field, term


def check_search(url, schedule, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, schedule[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: schedule[field]})
    assert_that(response.items, has_item(has_entry('id', schedule['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.schedule(name='sort1')
@fixtures.schedule(name='sort2')
def test_sort_offset_limit(schedule1, schedule2):
    url = confd.schedules.get
    yield s.check_sorting, url, schedule1, schedule2, 'name', 'sort'

    yield s.check_offset, url, schedule1, schedule2, 'name', 'sort'
    yield s.check_limit, url, schedule1, schedule2, 'name', 'sort'


@fixtures.schedule()
def test_get(schedule):
    response = confd.schedules(schedule['id']).get()
    assert_that(
        response.item,
        has_entries(
            id=schedule['id'],
            name=schedule['name'],
            timezone=schedule['timezone'],
            closed_destination=schedule['closed_destination'],
            open_periods=schedule['open_periods'],
            exceptional_periods=schedule['exceptional_periods'],
            enabled=schedule['enabled'],
            groups=empty(),
            incalls=empty(),
            outcalls=empty(),
            queues=empty(),
            users=empty(),
        ),
    )


@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.schedules(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Schedule'))

    response = confd.schedules(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.schedules.post(closed_destination={'type': 'none'})
    response.assert_created('schedules')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, id=not_(empty())))

    confd.schedules(response.item['id']).delete().assert_deleted()


def test_create_all_parameters():
    parameters = {
        'name': 'MySchedule',
        'timezone': 'American/Toronto',
        'closed_destination': {'type': 'hangup', 'cause': 'busy', 'timeout': 25},
        'open_periods': [
            {
                'hours_start': '07:15',
                'hours_end': '08:15',
                'week_days': [1, 2, 3, 4, 5],
                'month_days': [1, 15, 30],
                'months': [1, 6, 12],
            }
        ],
        'exceptional_periods': [
            {
                'hours_start': '07:25',
                'hours_end': '07:35',
                'week_days': [1, 2, 3, 4, 5],
                'month_days': [1, 30],
                'months': [1, 12],
                'destination': {'type': 'hangup', 'cause': 'congestion', 'timeout': 30},
            }
        ],
        'enabled': False,
    }

    response = confd.schedules.post(**parameters)
    response.assert_created('schedules')
    response = confd.schedules(response.item['id']).get()

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))

    confd.schedules(response.item['id']).delete().assert_deleted()


def test_create_open_periods_default_values():
    response = confd.schedules.post(
        open_periods=[{'hours_start': '07:15', 'hours_end': '08:15'}],
        closed_destination={'type': 'none'},
    )

    assert_that(
        response.item,
        has_entries(
            open_periods=contains(
                has_entries(
                    hours_start='07:15',
                    hours_end='08:15',
                    week_days=[1, 2, 3, 4, 5, 6, 7],
                    month_days=[
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                        9,
                        10,
                        11,
                        12,
                        13,
                        14,
                        15,
                        16,
                        17,
                        18,
                        19,
                        20,
                        21,
                        22,
                        23,
                        24,
                        25,
                        26,
                        27,
                        28,
                        29,
                        30,
                        31,
                    ],
                    months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                )
            )
        ),
    )

    confd.schedules(response.item['id']).delete().assert_deleted()


def test_create_exceptional_periods_default_values():
    response = confd.schedules.post(
        exceptional_periods=[
            {
                'hours_start': '07:15',
                'hours_end': '08:15',
                'destination': {'type': 'none'},
            }
        ],
        closed_destination={'type': 'none'},
    )

    assert_that(
        response.item,
        has_entries(
            exceptional_periods=contains(
                has_entries(
                    hours_start='07:15',
                    hours_end='08:15',
                    week_days=[1, 2, 3, 4, 5, 6, 7],
                    month_days=[
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                        9,
                        10,
                        11,
                        12,
                        13,
                        14,
                        15,
                        16,
                        17,
                        18,
                        19,
                        20,
                        21,
                        22,
                        23,
                        24,
                        25,
                        26,
                        27,
                        28,
                        29,
                        30,
                        31,
                    ],
                    months=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    destination={'type': 'none'},
                )
            )
        ),
    )

    confd.schedules(response.item['id']).delete().assert_deleted()


@fixtures.schedule()
def test_edit_minimal_parameters(schedule):
    response = confd.schedules(schedule['id']).put()
    response.assert_updated()


@fixtures.schedule()
def test_edit_all_parameters(schedule):
    parameters = {
        'name': 'MySchedule',
        'timezone': 'American/Toronto',
        'closed_destination': {'type': 'hangup', 'cause': 'busy', 'timeout': 25},
        'open_periods': [
            {
                'hours_start': '07:15',
                'hours_end': '08:15',
                'week_days': [1, 2, 3, 4, 5],
                'month_days': [1, 15, 30],
                'months': [1, 6, 12],
            }
        ],
        'exceptional_periods': [
            {
                'hours_start': '07:25',
                'hours_end': '07:35',
                'week_days': [1, 2, 3, 4, 5],
                'month_days': [1, 30],
                'months': [1, 12],
                'destination': {'type': 'hangup', 'cause': 'congestion', 'timeout': 30},
            }
        ],
        'enabled': False,
    }

    response = confd.schedules(schedule['id']).put(**parameters)
    response.assert_updated()

    response = confd.schedules(schedule['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.schedule()
@fixtures.ivr()
@fixtures.group()
@fixtures.outcall()
@fixtures.queue()
@fixtures.switchboard()
@fixtures.user()
@fixtures.voicemail()
@fixtures.conference()
@fixtures.skill_rule()
@fixtures.application()
@fixtures.moh()
def test_valid_destinations(schedule, *destinations):
    for destination in valid_destinations(*destinations):
        yield create_schedule_with_destination, destination
        yield update_schedule_with_destination, schedule['id'], destination


def create_schedule_with_destination(destination):
    response = confd.schedules.post(
        closed_destination=destination,
        exceptional_periods=[
            {'hours_start': '07:15', 'hours_end': '08:15', 'destination': destination}
        ],
    )
    response.assert_created('schedules')
    assert_that(
        response.item,
        has_entries(
            closed_destination=has_entries(**destination),
            exceptional_periods=has_items(
                has_entries(destination=has_entries(**destination))
            ),
        ),
    )

    confd.schedules(response.item['id']).delete().assert_deleted()


def update_schedule_with_destination(schedule_id, destination):
    response = confd.schedules(schedule_id).put(
        closed_destination=destination,
        exceptional_periods=[
            {'hours_start': '07:15', 'hours_end': '08:15', 'destination': destination}
        ],
    )
    response.assert_updated()
    response = confd.schedules(schedule_id).get()
    assert_that(
        response.item,
        has_entries(
            closed_destination=has_entries(**destination),
            exceptional_periods=has_items(
                has_entries(destination=has_entries(**destination))
            ),
        ),
    )


@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(main, sub):
    response = confd.schedules(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Schedule'))

    response = confd.schedules(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()


@fixtures.schedule()
def test_delete(schedule):
    response = confd.schedules(schedule['id']).delete()
    response.assert_deleted()
    response = confd.schedules(schedule['id']).get()
    response.assert_match(404, e.not_found(resource='Schedule'))


@fixtures.schedule(wazo_tenant=MAIN_TENANT)
@fixtures.schedule(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.schedules(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Schedule'))

    response = confd.schedules(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()


@fixtures.schedule()
def test_bus_events(schedule):
    url = confd.schedules(schedule['id'])
    body = {'closed_destination': {'type': 'none'}}
    headers = {'tenant_uuid': schedule['tenant_uuid']}

    yield s.check_event, 'schedule_created', headers, confd.schedules.post, body
    yield s.check_event, 'schedule_edited', headers, url.put
    yield s.check_event, 'schedule_deleted', headers, url.delete
