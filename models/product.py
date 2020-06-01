# -*- coding: utf-8 -*-
from openerp import models, fields, api, exceptions, _

class DoffProduct(models.Model):
    _inherit = "product.product"

    tipo_gas = fields.Selection([('diesel', 'Diesel'), ('regular', 'Regular'), ('super', 'Super'), ('kerosene', 'Kerosene')], string='Tipo Combustible')
