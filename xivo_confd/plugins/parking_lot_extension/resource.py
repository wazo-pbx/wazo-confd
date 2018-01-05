# -*- coding: UTF-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource


class ParkingLotExtensionItem(ConfdResource):

    def __init__(self, service, parking_lot_dao, extension_dao):
        super(ParkingLotExtensionItem, self).__init__()
        self.service = service
        self.parking_lot_dao = parking_lot_dao
        self.extension_dao = extension_dao

    @required_acl('confd.parkinglots.{parking_lot_id}.extensions.{extension_id}.delete')
    def delete(self, parking_lot_id, extension_id):
        parking_lot = self.parking_lot_dao.get(parking_lot_id)
        extension = self.extension_dao.get(extension_id)
        self.service.dissociate(parking_lot, extension)
        return '', 204

    @required_acl('confd.parkinglots.{parking_lot_id}.extensions.{extension_id}.update')
    def put(self, parking_lot_id, extension_id):
        parking_lot = self.parking_lot_dao.get(parking_lot_id)
        extension = self.extension_dao.get(extension_id)
        self.service.associate(parking_lot, extension)
        return '', 204
