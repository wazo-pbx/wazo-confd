# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class ConfigGenerator:
    def __init__(self, raw_generator):
        self.raw_generator = raw_generator

    def generate(self, device):
        configdevice = device.template_id or 'defaultconfigdevice'
        config = {
            'id': device.id,
            'configdevice': configdevice,
            'parent_ids': ['base', configdevice],
            'deletable': True,
            'raw_config': self.raw_generator.generate(device),
        }

        return config


class RawConfigGenerator:
    def __init__(self, generators):
        self.generators = generators

    def generate(self, device):
        raw_config = {'X_key': '', 'config_version': 1}

        for generator in self.generators:
            section = generator.generate(device)
            if section:
                raw_config.update(section)

        return raw_config


class UserGenerator:
    def __init__(self, device_db):
        self.device_db = device_db

    def generate(self, device):
        row = self.device_db.profile_for_device(device.id)
        if row:
            return {
                'X_xivo_user_uuid': row.uuid,
                'X_xivo_phonebook_profile': row.context,
            }


class ExtensionGenerator:
    def __init__(self, extension_dao):
        self.extension_dao = extension_dao

    def generate(self, device):
        return {
            'exten_dnd': self.find_exten('enablednd'),
            'exten_fwd_unconditional': self.find_exten('fwdunc'),
            'exten_fwd_no_answer': self.find_exten('fwdrna'),
            'exten_fwd_busy': self.find_exten('fwdbusy'),
            'exten_fwd_disable_all': self.find_exten('fwdundoall'),
            'exten_park': self.find_exten('parkext'),
            'exten_pickup_group': self.find_exten('pickupexten'),
            'exten_pickup_call': self.find_exten('pickup'),
            'exten_voicemail': self.find_exten('vmusermsg'),
        }

    def find_exten(self, typeval):
        extension = self.extension_dao.find_by(type='extenfeatures', typeval=typeval)
        if extension:
            return extension.clean_exten()


class FuncKeyGenerator:
    def __init__(
        self, user_dao, line_dao, user_line_dao, template_dao, device_dao, converters
    ):
        self.user_dao = user_dao
        self.line_dao = line_dao
        self.user_line_dao = user_line_dao
        self.device_dao = device_dao
        self.template_dao = template_dao
        self.converters = converters

    def generate(self, device):
        user, line = self.user_line_for_device(device.id)
        if user and line:
            template = self.get_unified_template(user)
            funckeys = self.convert_funckeys(user, line, template)
            return {'funckeys': funckeys}

    def user_line_for_device(self, device_id):
        lines = self.line_dao.find_all_by(device=device_id)
        try:
            line = min(lines, key=lambda x: x.position)
        except ValueError:
            return None, None

        main_user_line = self.user_line_dao.find_main_user_line(line.id)
        if main_user_line:
            user = self.user_dao.get(main_user_line.user_id)
            return user, line
        return None, None

    def get_unified_template(self, user):
        private_template = self.template_dao.get(user.private_template_id)
        if user.func_key_template_id:
            public_template = self.template_dao.get(user.func_key_template_id)
            return public_template.merge(private_template)
        return private_template

    def convert_funckeys(self, user, line, template):
        funckeys = {}
        for pos, funckey in template.keys.items():
            converter = self.converters[funckey.destination.type]
            funckeys.update(converter.build(user, line, pos, funckey))
        return funckeys


class SipGenerator:
    def __init__(self, registrar_dao, device_db):
        self.registrar_dao = registrar_dao
        self.device_db = device_db

    def generate(self, device):
        sip_lines = {}
        rows = self.device_db.sip_lines_for_device(device.id)
        for row in rows:
            pos = row.LineFeatures.position
            sip_lines[pos] = self.generate_sip_line(row)

        if len(sip_lines) > 0:
            return {'protocol': 'SIP', 'sip_lines': sip_lines}

    def generate_sip_line(self, row):
        line = row.LineFeatures
        sip = row.EndpointSIP
        extension = row.Extension
        registrar = self.registrar_dao.get(line.configregistrar)
        username, password = '', ''
        if sip._auth_section:
            for _, value in sip._auth_section.find('username'):
                username = value
                break
            for _, value in sip._auth_section.find('password'):
                password = value
                break

        config = {
            # 'auth_username': sip.name,  # TODO(pc-m): What does this map to?
            'auth_username': username,
            'username': username,
            'password': password,
            'display_name': line.caller_id_name,
            'number': extension.exten,
            'registrar_ip': registrar.main_host,
            'proxy_ip': registrar.proxy_main_host,
        }

        optional_keys = {
            'registrar_port': 'main_port',
            'proxy_port': 'proxy_main_port',
            'backup_proxy_ip': 'proxy_backup_host',
            'backup_proxy_port': 'proxy_backup_port',
            'backup_registrar_ip': 'backup_host',
            'backup_registrar_port': 'backup_port',
            'outbound_proxy_ip': 'outbound_proxy_host',
            'outbound_proxy_port': 'outbound_proxy_port',
        }

        for real_key, registrar_key in optional_keys.items():
            value = getattr(registrar, registrar_key, None)
            if value:
                config[real_key] = value

        return config


class SccpGenerator:
    def __init__(self, registrar_dao, line_dao):
        self.registrar_dao = registrar_dao
        self.line_dao = line_dao

    def generate(self, device):
        call_managers = {}

        line = self.line_dao.find_by(device=device.id, protocol='sccp')
        if line:
            registrar = self.registrar_dao.get(line.configregistrar)
            proxy_backup = registrar.proxy_backup_host

            call_managers['1'] = {'ip': registrar.proxy_main_host}
            if proxy_backup:
                call_managers['2'] = {'ip': proxy_backup}

        if len(call_managers) > 0:
            return {'protocol': 'SCCP', 'sccp_call_managers': call_managers}
