# -*- encoding: utf-8 -*-
from openerp import models, fields, api
class Compras(models.Model):
    _inherit = 'purchase.order'

    factura_cliente = fields.Char("Factura de Cliente")
