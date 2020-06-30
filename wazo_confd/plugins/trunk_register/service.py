# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.trunk import dao as trunk_dao_module

from .notifier import build_notifier_iax
from .validator import build_validator_iax


class TrunkRegisterService:
    def __init__(self, trunk_dao, validator, notifier):
        self.trunk_dao = trunk_dao
        self.validator = validator
        self.notifier = notifier


class TrunkRegisterIAXService(TrunkRegisterService):
    def associate(self, trunk, register):
        if trunk.register_iax is register:
            return

        self.validator.validate_association(trunk, register)
        self.trunk_dao.associate_register_iax(trunk, register)
        self.notifier.associated(trunk, register)

    def dissociate(self, trunk, register):
        if trunk.register_iax is not register:
            return

        self.validator.validate_dissociation(trunk, register)
        self.trunk_dao.dissociate_register_iax(trunk, register)
        self.notifier.dissociated(trunk, register)


def build_service_iax():
    return TrunkRegisterIAXService(
        trunk_dao_module, build_validator_iax(), build_notifier_iax()
    )
