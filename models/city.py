# -*- encoding: utf-8 -*-
from openerp import models, fields, api 


class Cities(models.Model):
    _name = "delivery.cities"

    def _getcountry(self):
        return self.env['res.country'].search([('name', '=', 'Honduras')]).id

    name = fields.Char("Ciudad", required=True)
    code = fields.Char("Código de Ciudad")
    departamento_id = fields.Many2one("res.country.state", "Departamento", required=True)
    activate = fields.Boolean("Ciudad Activa", default=True)
    country_id = fields.Many2one("res.country", "País", default=_getcountry)


class Pais(models.Model):
    _inherit ='res.country'

    departamento_ids = fields.One2many("res.country.state", "country_id", "Departamentos")


class Departamento(models.Model):
    _inherit = 'res.country.state'

    code = fields.Char("Código de Departamento", size=20, required=True)


class Destiny(models.Model):
    _name = "delivery.port.origin"

    name = fields.Char("Puerto del Origen", required=True)
    proveedor_id =fields.Many2one("res.partner", "Proveedor", domain=[('supplier','=',True),('transportista','!=',True)], required= True)
    descrption = fields.Text("Notas")
    activate = fields.Boolean("Pueto Activo", default=True)


