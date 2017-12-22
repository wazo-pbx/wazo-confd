# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from hamcrest import (
    assert_that,
    contains,
    contains_inanyorder,
    empty,
    equal_to,
    has_entries,
    has_items,
)

from ..helpers import errors as e
from ..helpers import fixtures
from ..helpers import scenarios as s
from . import BaseIntegrationTest
from . import confd, ari


def test_get_errors():
    fake_sound = confd.sounds('invalid').get
    yield s.check_resource_not_found, fake_sound, 'Sound'

    for invalid_name in ['.foo', 'foo/bar', '../bar']:
        response = confd.sounds(invalid_name).get()
        response.assert_status(404)


def test_delete_errors():
    fake_sound = confd.sounds('invalid').delete
    yield s.check_resource_not_found, fake_sound, 'Sound'


def test_post_errors():
    url = confd.sounds.post
    for check in error_checks(url):
        yield check

    for check in unique_error_checks(url):
        yield check


def error_checks(url):
    yield s.check_bogus_field_returns_error, url, 'name', True
    yield s.check_bogus_field_returns_error, url, 'name', 1234
    yield s.check_bogus_field_returns_error, url, 'name', s.random_string(150)
    yield s.check_bogus_field_returns_error, url, 'name', '.foo'
    yield s.check_bogus_field_returns_error, url, 'name', 'foo\nbar'
    yield s.check_bogus_field_returns_error, url, 'name', []
    yield s.check_bogus_field_returns_error, url, 'name', {}

    yield s.check_bogus_field_returns_error, url, 'name', 'system'


@fixtures.sound(name='unique')
def unique_error_checks(url, sound):
    yield s.check_bogus_field_returns_error, url, 'name', sound['name']


@fixtures.sound()
@fixtures.sound()
def test_list(sound1, sound2):
    response = confd.sounds.get()
    assert_that(response.items, has_items(
        sound1,
        sound2,
        has_entries(name='system'),
    ))


@fixtures.sound()
def test_get(sound):
    response = confd.sounds(sound['name']).get()
    assert_that(response.item, has_entries(name=sound['name'],
                                           files=empty()))


@fixtures.sound()
def test_get_with_files(sound):
    client = _new_sound_file_client()
    client.url.sounds(sound['name']).files('ivr.wav').put(content='ivrwav').assert_updated()
    client.url.sounds(sound['name']).files('ivr.ogg').put(content='ivrogg').assert_updated()

    response = confd.sounds(sound['name']).get()
    assert_that(response.item, has_entries(
        name=sound['name'],
        files=contains_inanyorder(has_entries(
            name='ivr',
            formats=contains_inanyorder(
                has_entries(format='wav',
                            language=None,
                            text=None),
                has_entries(format='ogg',
                            language=None,
                            text=None),
            )
        ))
    ))


def test_get_system_sound():
    sounds = [
        {'id': 'conf-now-unmuted',
         'formats': [{'language': 'fr_CA',
                      'format': 'slin'},
                     {'language': 'en_US',
                      'format': 'slin'},
                     {'language': 'en',
                      'format': 'gsm'}],
         'text': 'The conference is now unmuted.'},
    ]
    ari.set_sounds(sounds)

    response = confd.sounds('system').get()

    assert_that(response.item, has_entries(
        name='system',
        files=contains_inanyorder(has_entries(
            name=sounds[0]['id'],
            formats=contains_inanyorder(
                has_entries(format=sounds[0]['formats'][0]['format'],
                            language=sounds[0]['formats'][0]['language'],
                            text=None),
                has_entries(format=sounds[0]['formats'][1]['format'],
                            language=sounds[0]['formats'][1]['language'],
                            text=sounds[0]['text']),
                has_entries(format=sounds[0]['formats'][2]['format'],
                            language=sounds[0]['formats'][2]['language'],
                            text=sounds[0]['text']),
            )
        ))
    ))
    ari.reset()


def test_get_internal_folder():
    for name in ['monitor', 'recordings-meetme']:
        response = confd.sounds(name).get()
        response.assert_status(404)


def test_create_minimal_parameters():
    response = confd.sounds.post(name='sound1')
    response.assert_created('sound')

    assert_that(response.item, has_entries(name='sound1',
                                           files=empty()))

    confd.sounds(response.item['name']).delete().assert_deleted()


def test_create_all_parameters():
    test_create_minimal_parameters()


@fixtures.sound()
def test_edit_unimplemented(sound):
    response = confd.sounds(sound['name']).put()
    response.assert_status(405)


@fixtures.sound()
def test_delete(sound):
    response = confd.sounds(sound['name']).delete()
    response.assert_deleted()
    response = confd.sounds(sound['name']).get()
    response.assert_match(404, e.not_found(resource='Sound'))


def test_delete_system_sound():
    response = confd.sounds('system').delete()
    response.assert_status(400)


def test_delete_default_sound():
    for name in ['acd', 'features', 'playback', 'recordings']:
        response = confd.sounds(name).delete()
        response.assert_status(400)


def test_delete_internal_folder():
    for name in ['monitor', 'recordings-meetme']:
        response = confd.sounds(name).delete()
        response.assert_status(404)


@fixtures.sound()
def test_add_update_delete_filename(sound):
    client = _new_sound_file_client()

    # add a new file
    response = client.url.sounds(sound['name']).files('foo.wav').put(content='content is not checked')
    response.assert_status(204)

    response = client.url.sounds(sound['name']).files('foo.wav').get()
    assert_that(response.raw, equal_to('content is not checked'))

    response = confd.sounds(sound['name']).get()
    assert_that(response.item, has_entries(files=contains({'name': 'foo.wav'})))

    # update/overwrite the file
    response = client.url.sounds(sound['name']).files('foo.wav').put(content='some new content')
    response.assert_status(204)

    response = client.url.sounds(sound['name']).files('foo.wav').get()
    assert_that(response.raw, equal_to('some new content'))

    # delete the file
    response = client.url.sounds(sound['name']).files('foo.wav').delete()
    response.assert_deleted()

    response = confd.sounds(sound['name']).get()
    assert_that(response.item, has_entries(files=empty()))


@fixtures.sound()
def test_put_filename_errors(sound):
    client = _new_sound_file_client()
    filenames = [
        '.foo.wav',
        'foo/bar.wav',
        '../bar.wav',
    ]
    for filename in filenames:
        response = client.url.sounds(sound['name']).files(filename).put(content='content is not checked')
        response.assert_status(404)

    for invalid_name in ['.foo', 'foo/bar', '../bar']:
        response = client.url.sounds(invalid_name).files('foo.wav').put(content='content is not checked')
        response.assert_status(404)


def test_update_system_filename():
    client = _new_sound_file_client()
    response = client.url.sounds('system').files('foo.wav').put(content='content is not checked')
    response.assert_status(400)


def test_delete_system_filename():
    response = confd.sounds('system').files('foo.wav').delete()
    response.assert_status(400)


# XXX set this client in BaseIntegrationTest
def _new_sound_file_client():
    def encoder(data):
        if data is None:
            return None
        return data['content']

    return BaseIntegrationTest.new_client(headers={"Content-Type": "application/octet-stream",
                                                   "X-Auth-Token": "valid-token"}, encoder=encoder)


def test_bus_events():
    yield s.check_bus_event, 'config.sounds.created', confd.sounds.post, {'name': 'bus_event'}
    yield s.check_bus_event, 'config.sounds.deleted', confd.sounds('bus_event').delete
