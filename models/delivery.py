# -*- encoding: utf-8 -*-
from openerp import models, fields, api 


class DeliveryCostFleet(models.Model):
    _name = "delivery.cost.fleet"

    def _getcurrency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char("Lugar de Destino")
    long_kms = fields.Integer("Distancia (KMS)")
    origin_id = fields.Many2one("delivery.port.origin", "Lugar de Origen", required= True)
    destiny_id = fields.Many2one("delivery.cities", "Lugar de Destino", required= True)    
    costo_galon = fields.Float("Costo por Galon", required= True)
    transportista_id=fields.Many2one("res.partner", "Transportista", domain=[('transportista', '=', True)], required=True)
    activate=fields.Boolean("Activo", default=True)
    currency_id=fields.Many2one("res.currency","Moneda", default=_getcurrency)
    notas=fields.Text("Notas")

    @api.multi
    def write(self,vals):
        name_origin = self.env["delivery.port.origin"].browse(vals.get("origin_id")).name
        if not name_origin:
            name_origin = self.origin_id.name

        name_destiny= self.env["delivery.cities"].browse(vals.get("destiny_id")).name
        if not name_destiny:
            name_destiny = self.destiny_id.name
        vals["name"] = str(name_origin)  + "-" + str(name_destiny)
        return super(DeliveryCostFleet,self).write(vals)


    @api.model
    def create(self,vals):
        name_origin = self.env["delivery.port.origin"].browse(vals.get("origin_id")).name
        name_destiny = self.env["delivery.cities"].browse(vals.get("destiny_id")).name
        vals["name"] = name_origin + " - " + name_destiny
        return super(DeliveryCostFleet, self).create(vals)
