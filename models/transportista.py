# -*- encoding: utf-8 -*-
from openerp import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    transportista = fields.Boolean("Transportista", default=False)
    delivery_ids = fields.One2many("delivery.cost.fleet", "transportista_id", "Tarifa de Fletes")
    unidades_ids = fields.One2many("delivery.transportista.unidades", "transportista_id", "Unidades de Fletes")
    chofer_ids = fields.One2many("delivery.chofer", "transportista_id", "Choferes")
    supplier_combustible = fields.Boolean("Proveedor de combustible")


class Chofer(models.Model):
    _name = 'delivery.chofer'

    transportista_id = fields.Many2one("res.partner", "Transportista", domain=[('transportista', '=', True)])
    name = fields.Char("Chofer")
    id_chofer = fields.Char("Identidad de Chofer")
