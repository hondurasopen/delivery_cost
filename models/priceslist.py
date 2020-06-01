# -*- encoding: utf-8 -*-
from openerp import models, fields, api,_
from openerp.exceptions import except_orm, Warning, RedirectWarning


class Pricelist(models.Model):
    _name = "sale.priceslist.gas"

    product_id = fields.Many2one("product.product", "Producto", required=True)
    name = fields.Many2one("delivery.cities", "Ciudad", required=True)
    start_date = fields.Date("Fecha de Inicio", required=True)
    end_date = fields.Date("Fecha Final", required=True)
    price_list = fields.Float("Precio por galón", required=True, default=1)
    product_name = fields.Char("Tipo de Combustible")
    code = fields.Integer(help="Codigo auto-generado para identificar la ciudad", string="Codigo de Lista")
    notas = fields.Text("Notas")
    # Precio para ciudades que no estan en la lista de chevron
    ciudad_base_id = fields.Many2one("sale.priceslist.gas", "Ciudad Base")
    ciudad_adicional = fields.Boolean("Ciudad adicional")
    diferencia = fields.Float("Diferencia")
    price_list_base = fields.Float("Precio base", related="ciudad_base_id.price_list")

    _sql_constraints = [('code_uniq','Check(1=1)', 'Codigo debe ser unico!')]

    @api.model
    def create(self,vals):
        init_date=vals.get("start_date")
        fin_date= vals.get("end_date")
        if init_date >= fin_date:
            raise except_orm(_('Advertencia'), _('.Fecha de debe ser mayor a la fecha final'))
        return super(Pricelist,self).create(vals)

    @api.one
    def computeciudadesprecios(self):
        if self.ciudad_adicional:
            for x in self:
                self.price_list = self.price_list_base + self.diferencia

    @api.onchange("ciudad_base_id")
    def onchangeciudadbase(self):
        self.price_list_base = self.ciudad_base_id.price_list
