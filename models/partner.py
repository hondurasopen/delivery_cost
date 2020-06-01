# -*- encoding: utf-8 -*-
from openerp import fields, models, exceptions, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class Partner(models.Model):
    _inherit = 'res.partner'

    discount_invoice_ids = line_ids = fields.One2many("res.partner.discount", "obj_parent", "Descuento por Producto")
    discount_ciudad_ids = fields.One2many("res.partner.discount.ciudad", "cliente_id", "Descuentos por ciudad")
    activo_descuento_ciudad = fields.Boolean("Descuentos por ciudad")
    price_product_ids = fields.One2many("res.partner.cost.price", "obj_parent", "Precio de Costo")
    tipo_cliente = fields.Selection([('Distribuidoras', 'Distribuidoras'), ('Gasolinera', 'Gasolineras')], string='Tipo de Cliente')


class Costpriceline(models.Model):
    _name = "res.partner.cost.price"

    product_id = fields.Many2one("product.product", "Producto")
    cost = fields.Float("Precio de Costo")
    obj_parent = fields.Many2one("res.partner", "Proveedor")


class Discount_ciudad(models.Model):
    _name = "res.partner.discount.ciudad"

    ciudad_id = fields.Many2one("sale.priceslist.gas", "Ciudad", required=True)
    discount_ciudad = fields.Float("Descuento en ciudad")
    discount_total_city = fields.Float("Descuento Total en ciudad")
    product_id = fields.Many2one("product.product", "Producto", related="ciudad_id.product_id", required=True)
    cliente_id = fields.Many2one("res.partner", "Cliente con Descuento")


class Costpriceline(models.Model):
    _name = "res.partner.discount"

    product_id = fields.Many2one("product.product", "Producto")
    discount_invoice = fields.Float("Descuento en Facturas")
    discount_total = fields.Float("Descuento Total")
    obj_parent = fields.Many2one("res.partner", "Cliente con Descuento")
