# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from hamcrest import (
    all_of,
    assert_that,
    empty,
    has_entries,
    has_entry,
    has_item,
    has_items,
    is_not,
    none,
    not_,
)

from . import confd
from ..helpers import (
    associations as a,
    errors as e,
    fixtures,
    scenarios as s,
)
from ..helpers.config import MAIN_TENANT, SUB_TENANT


def test_get_errors():
    fake_trunk = confd.trunks(999999).get
    yield s.check_resource_not_found, fake_trunk, 'Trunk'


def test_delete_errors():
    fake_trunk = confd.trunks(999999).delete
    yield s.check_resource_not_found, fake_trunk, 'Trunk'


def test_post_errors():
    url = confd.trunks.post
    for check in error_checks(url):
        yield check


@fixtures.trunk()
def test_put_errors(trunk):
    url = confd.trunks(trunk['id']).put
    for check in error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'context', 123
    yield s.check_bogus_field_returns_error, url, 'context', []
    yield s.check_bogus_field_returns_error, url, 'context', {}
    yield s.check_bogus_field_returns_error, url, 'context', 'invalid'
    yield s.check_bogus_field_returns_error, url, 'twilio_incoming', 123
    yield s.check_bogus_field_returns_error, url, 'twilio_incoming', []
    yield s.check_bogus_field_returns_error, url, 'twilio_incoming', {}


@fixtures.context(label='search')
@fixtures.context(label='hidden')
@fixtures.sip(name='name_search', label='label_search')
@fixtures.iax(name='name_search')
@fixtures.custom(interface='name_search')
def test_search(search_ctx, hidden_ctx, sip, iax, custom):
    @fixtures.trunk(context=search_ctx['name'])
    @fixtures.trunk(context=hidden_ctx['name'])
    def aux(trunk, hidden):
        url = confd.trunks
        searches = {'context': 'search'}

        for field, term in searches.items():
            yield check_search, url, trunk, hidden, field, term

        searches = {'name': 'name_search', 'label': 'label_search'}
        with a.trunk_endpoint_sip(trunk, sip):
            for field, term in searches.items():
                yield check_relation_search, url, trunk, hidden, field, term

        searches = {'name': 'name_search'}
        with a.trunk_endpoint_iax(trunk, iax):
            for field, term in searches.items():
                yield check_relation_search, url, trunk, hidden, field, term

        searches = {'name': 'name_search'}
        with a.trunk_endpoint_custom(trunk, custom):
            for field, term in searches.items():
                yield check_relation_search, url, trunk, hidden, field, term

    aux()


def check_search(url, trunk, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry(field, trunk[field])))
    assert_that(response.items, is_not(has_item(has_entry(field, hidden[field]))))

    response = url.get(**{field: trunk[field]})
    assert_that(response.items, has_item(has_entry('id', trunk['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


def check_relation_search(url, trunk, hidden, field, term):
    response = url.get(search=term)
    assert_that(response.items, has_item(has_entry('id', trunk['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))

    response = url.get(**{field: term})
    assert_that(response.items, has_item(has_entry('id', trunk['id'])))
    assert_that(response.items, is_not(has_item(has_entry('id', hidden['id']))))


@fixtures.context(label='sort1')
@fixtures.context(label='sort2')
def test_sorting_offset_limit(ctx1, ctx2):
    @fixtures.trunk(context=ctx1['name'])
    @fixtures.trunk(context=ctx2['name'])
    def aux(trunk1, trunk2):
        url = confd.trunks.get
        yield s.check_sorting, url, trunk1, trunk2, 'context', 'sort'
        yield s.check_offset, url, trunk1, trunk2, 'context', 'sort'
        yield s.check_limit, url, trunk1, trunk2, 'context', 'sort'

    aux()


@fixtures.trunk(wazo_tenant=MAIN_TENANT)
@fixtures.trunk(wazo_tenant=SUB_TENANT)
def test_list_multi_tenant(main, sub):
    response = confd.trunks.get(wazo_tenant=MAIN_TENANT)
    assert_that(response.items, all_of(has_item(main)), not_(has_item(sub)))

    response = confd.trunks.get(wazo_tenant=SUB_TENANT)
    assert_that(response.items, all_of(has_item(sub), not_(has_item(main))))

    response = confd.trunks.get(wazo_tenant=MAIN_TENANT, recurse=True)
    assert_that(response.items, has_items(main, sub))


@fixtures.trunk()
def test_get(trunk):
    response = confd.trunks(trunk['id']).get()
    assert_that(
        response.item,
        has_entries(
            id=trunk['id'],
            context=trunk['context'],
            twilio_incoming=trunk['twilio_incoming'],
            endpoint_sip=none(),
            endpoint_custom=none(),
            endpoint_iax=none(),
            outcalls=empty(),
            register_iax=none(),
        ),
    )


@fixtures.trunk(wazo_tenant=MAIN_TENANT)
@fixtures.trunk(wazo_tenant=SUB_TENANT)
def test_get_multi_tenant(main, sub):
    response = confd.trunks(main['id']).get(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Trunk'))

    response = confd.trunks(sub['id']).get(wazo_tenant=MAIN_TENANT)
    assert_that(response.item, has_entries(**sub))


def test_create_minimal_parameters():
    response = confd.trunks.post()
    response.assert_created('trunks')

    assert_that(response.item, has_entries(id=not_(empty()), tenant_uuid=MAIN_TENANT))


@fixtures.context()
def test_create_all_parameters(context):
    parameters = {'context': context['name'], 'twilio_incoming': True}
    response = confd.trunks.post(**parameters)
    response.assert_created('trunks')

    assert_that(response.item, has_entries(tenant_uuid=MAIN_TENANT, **parameters))


@fixtures.context(wazo_tenant=MAIN_TENANT)
def test_create_multi_tenant(context):
    response = confd.trunks.post(context=context['name'], wazo_tenant=SUB_TENANT)
    response.assert_match(400, e.different_tenant())


@fixtures.trunk()
def test_edit_minimal_parameters(trunk):
    parameters = {}

    response = confd.trunks(trunk['id']).put(**parameters)
    response.assert_updated()


@fixtures.context(label='not_default')
@fixtures.trunk()
def test_edit_all_parameters(context, trunk):
    parameters = {'context': context['name'], 'twilio_incoming': True}

    response = confd.trunks(trunk['id']).put(**parameters)
    response.assert_updated()

    response = confd.trunks(trunk['id']).get()
    assert_that(response.item, has_entries(parameters))


@fixtures.context()
@fixtures.trunk(wazo_tenant=MAIN_TENANT)
@fixtures.trunk(wazo_tenant=SUB_TENANT)
def test_edit_multi_tenant(context, main, sub):
    response = confd.trunks(main['id']).put(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Trunk'))

    response = confd.trunks(sub['id']).put(wazo_tenant=MAIN_TENANT)
    response.assert_updated()

    response = confd.trunks(sub['id']).put(
        context=context['name'], wazo_tenant=MAIN_TENANT
    )
    response.assert_match(400, e.different_tenant())


@fixtures.trunk()
def test_delete(trunk):
    response = confd.trunks(trunk['id']).delete()
    response.assert_deleted()


@fixtures.trunk(wazo_tenant=MAIN_TENANT)
@fixtures.trunk(wazo_tenant=SUB_TENANT)
def test_delete_multi_tenant(main, sub):
    response = confd.trunks(main['id']).delete(wazo_tenant=SUB_TENANT)
    response.assert_match(404, e.not_found(resource='Trunk'))

    response = confd.trunks(sub['id']).delete(wazo_tenant=MAIN_TENANT)
    response.assert_deleted()
