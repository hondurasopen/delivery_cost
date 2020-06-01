# -*- encoding: utf-8 -*-
from openerp import models, fields, api, exceptions, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class DeliveryLiquidacion(models.Model):
    _name = "vedd.cost.fleet.liquidacion"
    _rec_name = "start_date"
    _order = "start_date asc"

    start_date = fields.Date("Fecha de inicio", required=True)
    end_date = fields.Date("Fecha final", required=True)
    amount_total = fields.Float("Total LPS")
    supplier_id = fields.Many2one("res.partner", "Proveedor", required=True)
    flete_ids = fields.One2many("vedd.cost.fleet.liquidacion.line", "parent_id", "Detail")
    state = fields.Selection( [('draft', 'Borrador'), ('done', 'Liquidado')], string="Estado", default='draft')
    invoice_id = fields.Many2one("account.invoice", "Factura")
    invoice_number = fields.Char("# Factura")


    @api.multi
    def unlink(self):
        if (self.state == 'done'):
            raise exceptions.Warning(_('Error:: No se puede borrar registros validados.'))
        return super(DeliveryLiquidacion, self).unlink()


    @api.multi
    def create_invoice(self):
        if not self.invoice_number:
            raise exceptions.Warning(_('Error:: Debe de ingresar el numero de factura del proveedor.'))
        delivery_line_obj = self.env["sale.order.line.delivery"]
        inv_obj = self.env['account.invoice']
        inv_line_obj = self.env['account.invoice.line']
        values = {}
        vals = {}
        journal_id = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        partner_id = 0
        invoice_id = 0
        values = {
            'partner_id': self.supplier_id.id,
            'date_invoice': self.end_date,
            'account_id': self.supplier_id.property_account_payable.id,
            'type': 'in_invoice',
            'journal_id': journal_id.id,
            'supplier_invoice_number': self.invoice_number,
            'origin': 'Liquidación de fletes'
        }
        invoice_id = inv_obj.create(values)
        if invoice_id:
            acc_id = journal_id.default_debit_account_id.id
            vals = {
                'name': 'Liquidación de fletes',
                'invoice_id': invoice_id.id,
                'account_id': acc_id,
                'price_unit': self.amount_total or 0.0,
                'quantity': 1,
            }
            inv_line_id = inv_line_obj.create(vals)
            if inv_line_id:
                self.invoice_id = invoice_id.id
                self.set_liquidacion()
        return


    @api.multi
    def set_liquidacion(self):
        if self.flete_ids:
            self.write({'state': 'done'})


    @api.multi
    def get_fletes_sale(self):
        if self.start_date > self.end_date:
            raise Warning(_('La fecha de inicio es mayor fecha final'))
        state_sale = []
        state_sale.append('manual')
        state_sale.append('progress')
        state_sale.append('shipping_except')
        state_sale.append('invoice_except')
        state_sale.append('done')
        if self.flete_ids:
            self.flete_ids.unlink()

        sale_ids = self.env["sale.order"].search([('date_order', '>=', self.start_date), ('date_order', '<=', self.end_date), ('state', 'in', tuple(state_sale))])
        for sale in sale_ids:
            for delivery in sale.sale_line_fleet_ids:
                if delivery.transportista_id.id == self.supplier_id.id:
                    obj_report_fleet = self.env["vedd.cost.fleet.liquidacion.line"]
                    vals = {
                        'order_id': sale.id,
                        'parent_id': self.id,
                        'flete_id': delivery.id,
                        'numero_tanque': delivery.name.name,
                        'destinity': delivery.fletes_id.id,
                        'date_delivery': sale.date_order,
                        'customer_id': sale.partner_id.id,
                        'product_id': delivery.product_id.id,
                        'qty_galones': delivery.qty_galones,
                        'costo_galon': delivery.costo_galon,
                        'total': delivery.total,
                    }
                    if sale.invoice_ids.state in ('open', 'paid'):
                        vals['invoice_id']: sale.invoice_ids.number
                    id_obj = obj_report_fleet.create(vals)

        self.amount_total = 0
        self.get_total()


    def get_total(self):
        if self.flete_ids:
            for x in self.flete_ids:
                self.amount_total += x.total


class DeliveryLiquidacionLine(models.Model):
    _name = "vedd.cost.fleet.liquidacion.line"
    _rec_name = "numero_tanque"
    _order = "date_delivery asc"


    order_id = fields.Many2one("sale.order", "Venta")
    parent_id = fields.Many2one("vedd.cost.fleet.liquidacio", "Parent")
    invoice_id = fields.Char("Factura")
    customer_id = fields.Many2one("res.partner", "Cliente")
    product_id = fields.Many2one("product.product", "Producto")
    date_delivery = fields.Date("Fecha")
    numero_tanque = fields.Char("# Pipa")
    destinity = fields.Many2one("delivery.cost.fleet", "Destino")
    qty_galones = fields.Float("Galones")
    costo_galon = fields.Float("Costo x Galón")
    total = fields.Float("Total")
    flete_id = fields.Many2one("sale.order.line.delivery", "Flete")