# Copyright 2013-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests

from xivo_dao.resources.configuration import dao as configuration_dao


class SysconfdError(Exception):
    def __init__(self, code, value):
        self.code = code
        self.value = value

    def __str__(self):
        return f"sysconfd error: status {self.code} - {self.value}"


class SysconfdPublisher:
    @classmethod
    def from_config(cls, config):
        url = "http://{}:{}".format(
            config['sysconfd']['host'], config['sysconfd']['port']
        )
        return cls(url, configuration_dao)

    def __init__(self, base_url, dao):
        self.base_url = base_url
        self.dao = dao
        self._reset()

    def exec_request_handlers(self, args):
        if self.dao.is_live_reload_enabled():
            self.add_handlers(args)

    def add_handlers(self, args):
        self.handlers_contexts.extend(args.pop('context', []))
        for service, new_commands in args.items():
            commands = self.handlers.setdefault(service, set())
            commands.update(set(new_commands))

    def move_voicemail(self, old_number, old_context, number, context):
        params = {
            'old_mailbox': old_number,
            'old_context': old_context,
            'new_mailbox': number,
            'new_context': context,
        }
        url = f"{self.base_url}/move_voicemail"
        self.add_request('GET', url, params=params)

    def delete_voicemail(self, number, context):
        params = {'mailbox': number, 'context': context}
        url = f"{self.base_url}/delete_voicemail"
        self.add_request('GET', url, params=params)

    def commonconf_apply(self):
        url = f"{self.base_url}/commonconf_apply"
        self.add_request('GET', url)

    def commonconf_generate(self):
        url = f"{self.base_url}/commonconf_generate"
        self.add_request('POST', url, json={})

    def set_hosts(self, hostname, domain):
        data = {'hostname': hostname, 'domain': domain}
        url = f"{self.base_url}/hosts"
        self.add_request('POST', url, json=data)

    def set_resolvconf(self, nameserver, domain):
        data = {'nameservers': nameserver, 'search': [domain]}
        url = f"{self.base_url}/resolv_conf"
        self.add_request('POST', url, json=data)
        self.flush()

    def service_action(self, service_name, action):
        data = {service_name: action}
        url = f"{self.base_url}/services"
        self.add_request('POST', url, json=data)

    def restart_provd(self):
        self.service_action('wazo-provd', 'restart')

    def restart_phoned(self):
        self.service_action('wazo-phoned', 'restart')

    def dhcpd_update(self):
        url = f"{self.base_url}/dhcpd_update"
        self.add_request('GET', url)

    def xivo_service_start(self):
        data = {'wazo-service': 'start'}
        url = f"{self.base_url}/xivoctl"
        self.add_request('POST', url, json=data)

    def xivo_service_enable(self):
        data = {'wazo-service': 'enable'}
        url = f"{self.base_url}/xivoctl"
        self.add_request('POST', url, json=data)

    def get_ha_config(self):
        session = self._session()
        url = f"{self.base_url}/get_ha_config"
        return session.get(url).json()

    def update_ha_config(self, ha):
        url = f"{self.base_url}/update_ha_config"
        self.add_request('POST', url, json=ha)

    def _session(self):
        session = requests.Session()
        session.trust_env = False
        return session

    def check_for_errors(self, response):
        if response.status_code != 200:
            raise SysconfdError(response.status_code, response.text)

    def add_request(self, *args, **kwargs):
        self.requests.append(lambda session: session.request(*args, **kwargs))

    def flush(self):
        session = self._session()
        self.flush_handlers(session)
        self.flush_requests(session)
        self._reset()

    def flush_handlers(self, session):
        if len(self.handlers) > 0:
            url = f"{self.base_url}/exec_request_handlers"
            body = {key: tuple(commands) for key, commands in self.handlers.items()}
            if self.handlers_contexts:
                body['context'] = self.handlers_contexts
            response = session.request('POST', url, json=body)
            self.check_for_errors(response)

    def flush_requests(self, session):
        for request_applicator in self.requests:
            response = request_applicator(session)
            self.check_for_errors(response)

    def rollback(self):
        self._reset()

    def _reset(self):
        self.requests = []
        self.handlers = {}
        self.handlers_contexts = []
