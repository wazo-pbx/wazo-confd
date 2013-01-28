#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
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


from distutils.core import setup

setup(
    name='xivo-restapid',
    version='0.1',
    description='XIVO REST API daemon',
    author='Avencall',
    author_email='xivo-dev@lists.proformatique.com',
    url='http://wiki.xivo.fr/',
    license='GPLv3',
    packages=['xivo_restapi',
              'xivo_restapi.dao',
              'xivo_restapi.dao.helpers',
              'xivo_restapi.rest',
              'xivo_restapi.services'],
    scripts=['bin/xivo_recording_agi.py'],
    data_files=[('/usr/bin', ['bin/xivo-restapid']),
                ('/etc/init.d', ['etc/init.d/xivo-restapid']),
                ('/etc/asterisk/extensions_extra.d/', ['etc/asterisk/extensions_extra.d/xivo-recording.conf']),
                ('/etc/nginx/sites-enabled', ['etc/nginx/sites-enabled/restapi'])]
)
