# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from flask import Blueprint

from xivo_dao.resources.extension.model import Extension

from xivo_confd import config
from xivo_confd.helpers.converter import Converter
from xivo_confd.helpers.mooltiparse import Field, Int, Unicode, Boolean
from xivo_confd.helpers.resource import CRUDResource, DecoratorChain

from xivo_confd.resources.extensions import services


def load(core_rest_api):
    blueprint = Blueprint('extensions',
                          __name__,
                          url_prefix='/%s/extensions' % config.API_VERSION)

    document = core_rest_api.content_parser.document(
        Field('id', Int()),
        Field('exten', Unicode()),
        Field('context', Unicode()),
        Field('commented', Boolean())
    )
    converter = Converter.resource(document, Extension)

    provd_client = core_rest_api.provd_client()
    service = services.build_service(provd_client)

    resource = CRUDResource(service, converter, list(document.field_names()) + ['type'])

    DecoratorChain.register_scrud(core_rest_api, blueprint, resource)
