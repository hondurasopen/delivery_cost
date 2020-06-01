# -*- encoding: utf-8 -*-
from openerp import models, fields, api
class Invoiceaddress(models.Model):
    _inherit = 'account.invoice'

    @api.one
    def _compute_check(self):
        if self.state == 'open' and self.type == 'out_invoice':
            if self.amount_total == self.importe_abonado:
                query = """ UPDATE account_invoice SET state='paid' WHERE id = %s"""
                self._cr.execute(query, (self.id,))
                self.check_status = True

    @api.one
    def _compute_get_nota(self):
        if self.type == 'out_invoice':
            inv_obj_refund = self.env["account.invoice"].search([('type', '=', 'out_refund'), ('origin', '=', self.number)])
            if inv_obj_refund:
                for refund in inv_obj_refund:
                    if refund.state == 'open' or refund.state == 'paid':
                        self.total_ncredito += refund.amount_total

    optional_address = fields.Text("Dirección de Factura", help="Si existe direeción de facturación, esta sera la dirección que se mostrara en la factura")
    total_ncredito = fields.Float("Total de Nota de Credito", domain=[('type','=','out_invoice')], compute='_compute_get_nota')
    check_status = fields.Boolean("Factura Pagada",  compute='_compute_check')
    nota_debito = fields.Boolean("Nota de Debito")
    tipo_nota_credito = fields.Many2one("tipo.nota.debito.factura", "Tipo nota crédito")
