# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class Unidades(models.Model):
    _name = "delivery.transportista.unidades"

    def _getcurrency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char("Tanque", required=True)
    capacidad = fields.Integer("Capacidad (Gals)", required=True)
    transportista_id = fields.Many2one("res.partner", "Transportista", domain=[('transportista','=',True)], required=True)
    dep1 = fields.Char("Deposito 1")
    dep2 = fields.Char("Deposito 2")
    dep3 = fields.Char("Deposito 3")
    dep4 = fields.Char("Deposito 4")
    dep5 = fields.Char("Deposito 5")
    dep6 = fields.Char("Deposito 6")
    numero_placa = fields.Char("Número de Placa")
    deposito_ids = fields.One2many("delivery.transportista.unidades.depositos", "unidad_id", "Depósitos")

class UnidadesDeposito(models.Model):
	_name = "delivery.transportista.unidades.depositos"

	unidad_id = fields.Many2one("delivery.transportista.unidades", "Unidad")
	name = fields.Char("Capacidad", required=True)
	deposito = fields.Char("Depósito")
