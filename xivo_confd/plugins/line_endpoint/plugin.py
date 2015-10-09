# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_confd.plugins.line_endpoint.service import build_service
from xivo_confd.plugins.line_endpoint.resource import LineEndpointAssociation
from xivo_confd.plugins.line_endpoint.resource import LineEndpointGet
from xivo_confd.plugins.line_endpoint.resource import EndpointLineGet


class Plugin(object):

    def load(self, core):
        api = core.api
        service = build_service()

        api.add_resource(LineEndpointAssociation,
                         '/lines/<int:line_id>/endpoints/sip/<int:endpoint_id>',
                         endpoint='line_endpoints',
                         resource_class_args=(service,)
                         )

        api.add_resource(LineEndpointGet,
                         '/lines/<int:line_id>/endpoints/sip',
                         resource_class_args=(service,)
                         )

        api.add_resource(EndpointLineGet,
                         '/endpoints/sip/<int:endpoint_id>/lines',
                         resource_class_args=(service,)
                         )
