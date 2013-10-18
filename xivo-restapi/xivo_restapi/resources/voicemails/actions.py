# -*- coding: UTF-8 -*-

import logging

from flask.globals import request
from flask.blueprints import Blueprint
from flask.helpers import make_response, url_for

from xivo_restapi import config
from xivo_restapi.helpers.route_generator import RouteGenerator
from xivo_restapi.helpers.formatter import Formatter
from xivo_restapi.resources.voicemails import mapper
from xivo_restapi.helpers import serializer
from xivo_restapi.helpers.common import extract_find_parameters
from xivo_dao.data_handler.voicemail.model import Voicemail, VoicemailOrder
from xivo_dao.data_handler.voicemail import services as voicemail_services


logger = logging.getLogger(__name__)
blueprint = Blueprint('voicemails', __name__, url_prefix='/%s/voicemails' % config.VERSION_1_1)
route = RouteGenerator(blueprint)
formatter = Formatter(mapper, serializer, Voicemail)

order_mapping = {
    'name': VoicemailOrder.name,
    'number': VoicemailOrder.number,
    'context': VoicemailOrder.context,
    'email': VoicemailOrder.email,
    'language': VoicemailOrder.language,
    'timezone': VoicemailOrder.timezone
}


@route('')
def list():
    find_parameters = extract_find_parameters(order_mapping)
    search_result = voicemail_services.find_all(**find_parameters)
    result = formatter.list_to_api(search_result.items, search_result.total)
    return make_response(result, 200)


@route('/<int:voicemailid>')
def get(voicemailid):
    voicemail = voicemail_services.get(voicemailid)
    result = formatter.to_api(voicemail)
    return make_response(result, 200)


@route('', methods=['POST'])
def create():
    data = request.data.decode("utf-8")
    voicemail = formatter.to_model(data)
    voicemail = voicemail_services.create(voicemail)
    result = formatter.to_api(voicemail)
    location = url_for('.get', voicemailid=voicemail.id)
    return make_response(result, 201, {'Location': location})
