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

from xivo_confd.plugins.user_lines.service import build_service
from xivo_confd.plugins.user_lines.resource import UserLineList, UserLineItem


class Plugin(object):

    def load(self, core):
        api = core.api
        service = build_service()

        api.add_resource(UserLineItem,
                         '/users/<int:user_id>/lines/<int:line_id>',
                         endpoint='user_lines',
                         resource_class_args=(service,)
                         )
        api.add_resource(UserLineList,
                         '/users/<int:user_id>/lines',
                         resource_class_args=(service,)
                         )
