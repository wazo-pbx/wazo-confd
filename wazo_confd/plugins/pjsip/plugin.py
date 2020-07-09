# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import gzip
import json

from .service import build_service, build_pjsip_transport_service
from .resource import (
    PJSIPDocList,
    PJSIPGlobalList,
    PJSIPSystemList,
    PJSIPTransportItem,
    PJSIPTransportList,
)
from .exceptions import PJSIPDocError
from . import schema

logger = logging.getLogger(__name__)


class PJSIPDoc:
    _internal_fields = set(['type'])

    def __init__(self, filename):
        logger.debug('%s initialized with file %s', self.__class__.__name__, filename)
        self._filename = filename
        self._content = None

    def get(self):
        return self.content

    def is_valid_in_section(self, section_name, variable):
        return variable in self.get_section_variables(section_name)

    def get_section_variables(self, section_name):
        return self.content.get(section_name, {}).keys()

    @property
    def content(self):
        if self._content is None:
            self._content = self._fetch()
            for section_name in self._content.keys():
                for field in self._internal_fields:
                    self._content[section_name].pop(field, None)
        return self._content

    def _fetch(self):
        try:
            logger.debug(
                'refreshing %s cached file from %s',
                self.__class__.__name__,
                self._filename,
            )
            with gzip.open(self._filename, 'rb') as f:
                return json.load(f)
        except Exception as e:
            logger.info('failed to read PJSIP doc %s %s', self._filename, e)
            raise PJSIPDocError('failed to read PJSIP JSON documentation')


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        config = dependencies['config']

        pjsip_doc = PJSIPDoc(config['pjsip_config_doc_filename'])
        service = build_service(pjsip_doc)
        transport_service = build_pjsip_transport_service(
            pjsip_doc, schema.PJSIPTransportSchema()
        )

        api.add_resource(
            PJSIPDocList, '/asterisk/pjsip/doc', resource_class_args=(pjsip_doc,),
        )

        api.add_resource(
            PJSIPGlobalList, '/asterisk/pjsip/global', resource_class_args=(service,),
        )

        api.add_resource(
            PJSIPSystemList, '/asterisk/pjsip/system', resource_class_args=(service,),
        )

        api.add_resource(
            PJSIPTransportList,
            '/sip/transports',
            resource_class_args=(transport_service,),
        )

        api.add_resource(
            PJSIPTransportItem,
            '/sip/transports/<uuid:transport_uuid>',
            endpoint='sip_transports',
            resource_class_args=(transport_service,),
        )
