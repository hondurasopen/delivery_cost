# -*- encoding: utf-8 -*-
from openerp import models, fields, api,_
from openerp.exceptions import except_orm, Warning, RedirectWarning


class Pricelistdata(models.Model):
    _name = "sale.priceslist.import.data"

    name = fields.Char("Lista de Precio")
    product_id = fields.Many2one("product.product", "Producto")
    inicio_date = fields.Date("Fecha de Inicio", readonly=True)
    final_date = fields.Date("Fecha Final", readonly=True)
    line_ids = fields.One2many("sale.priceslist.import.data.line", "obj_parent", "Precios por Ciudad")
    state = fields.Selection( [('draft', 'Borrador'), ('done', 'Actulizado')], string="Estado", default='draft')

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_update(self):
        if not self.line_ids:
            raise except_orm(_('Advertencia'), _('.No Existe Ciudades para actualizar precios!!!'))
        else:
            obj_priceslist = self.env["sale.priceslist.gas"]
            for line in self.line_ids:
                tmp_code = obj_priceslist.search([("code","=",line.code), ('product_id', '=', line.product_id.id)])
                if tmp_code:
                    tmp_code.write({'price_list': line.price_list, 'start_date': line.date_init, 'end_date': line.date_final})
            self.write({'state': 'done'})
            obj_update_l = self.env["sale.priceslist.gas"].search([('ciudad_base_id', '>', 1)])
            for obj in obj_update_l:
                obj.price_list = obj.price_list_base + obj.diferencia


	#@api.model
	#def create(self,vals):
		#init_date=vals.get("inicio_date")
		#fin_date= vals.get("final_date")
		#if init_date >= fin_date:
			#raise except_orm(_('Advertencia'), _('.Fecha de debe ser mayor a la fecha final'))
		#return super(Pricelistdata,self).create(vals)
