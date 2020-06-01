# -*- encoding: utf-8 -*-
from openerp import models, fields, api,_
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerp.addons.decimal_precision as dp


class CostPrice(models.Model):
    _name = "purchase.cost.price"

    name = fields.Char("Precio de Costo")
    inicio_date = fields.Date("Fecha de Inicio", required=True)
    final_date = fields.Date("Fecha Final", required=True)
    line_ids = fields.One2many("purchase.cost.price.line", "obj_parent", "Precios de Costo")
    state = fields.Selection( [('draft', 'Borrador'), ('done', 'Actulizado')], string="Estado", default='draft')
    # CAMBIO NUEVO
    proveedor_id = fields.Many2one("res.partner", "Proveedor", domain=[('supplier','=',True), ('transportista','=',False)])

    @api.multi
    def action_update_cost(self):
        if not self.line_ids:
            raise except_orm(_('Advertencia'), _('.No Existe productos a actualizar'))
        else:
            """obj_product = self.env["product.product"]
            for line in self.line_ids:
                tmp_product = obj_product.search([("id", "=", line.product_id.id)])
                if tmp_product:
                    tmp_product.write({'standard_price': line.cost_price})
            self.write({'state': 'done'})"""
            obj_proveedor = self.env["res.partner"]
            for product in self.proveedor_id.price_product_ids:
                for line in self.line_ids:
                    if line.product_id.id == product.product_id.id:
                        product.write({'cost':line.cost_price})
            self.write({'state': 'done'})


class Costpriceline(models.Model):
    _name = "purchase.cost.price.line"

    product_id = fields.Many2one("product.product", "Producto")
    cost_price = fields.Float("Precio de Costo Nuevo", digits_compute=dp.get_precision('Product Price'))
    cost_price_old = fields.Float("Precio de Costo anterior", digits_compute=dp.get_precision('Product Price'))
    obj_parent = fields.Many2one("purchase.cost.price", "Costo")
    proveedor_id = fields.Many2one("res.partner", "Proveedor", domain=[('supplier','=',True)])

    @api.onchange("product_id")
    def onchangeproduct(self):
        self.cost_price_old = self.product_id.standard_price

