# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class Saleline(models.Model):
    _inherit = 'sale.order.line'

    ruta = fields.Many2one("sale.priceslist.gas", "Ruta")

    @api.multi
    def product_id_change(self, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True,date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        res = super(Saleline, self).product_id_change(pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
        obj_partner = self.env["res.partner"].search([('id', '=', partner_id)])
        for prod in obj_partner.discount_invoice_ids:
            if prod.product_id.id == product:
                res["value"]["discount"] = prod.discount_invoice
        return res

    #AQUI ESTA LA SOLUCION PARA GENERAR LOS PRECIOS AL SELECCIONAR LA RUTA

    @api.onchange("ruta")
    def onchangeruta(self):
        # for order in self.order_id:
        # if order.date_order >= self.ruta.start_date and order.date_order <= self.ruta.end_date:
        self.price_unit = self.ruta.price_list
        if self.order_id.partner_id.activo_descuento_ciudad and self.order_id.partner_id.discount_ciudad_ids:
            for line_ciudad in self.order_id.partner_id.discount_ciudad_ids:
                if line_ciudad.ciudad_id.id == self.ruta.id:
                    self.discount = line_ciudad.discount_ciudad

        if self.order_id.proveedor_combustible_id:
            for product_ids in self.order_id.proveedor_combustible_id.price_product_ids:
                if self.product_id.id == product_ids.product_id.id:
                    self.purchase_price = product_ids.cost
        product_obj = self.env['product.product'].search([('id', '=', self.product_id.id)])
        product_obj.write({'list_price': self.ruta.price_list})
