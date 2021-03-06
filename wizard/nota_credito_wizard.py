from openerp import fields, models, exceptions, api, _
import base64
import csv
import cStringIO
from openerp.exceptions import except_orm, Warning, RedirectWarning


class NotaCreditoWizard(models.TransientModel):
    _name = "nota.credito.wizard"


    fecha_nota = fields.Date(string="Fecha de Inicio", required=True)
    periodo_id =fields.Many2one('account.period', 'Periodo')
    journal_id = fields.Many2one('account.journal', 'Diario de Nota de Credito', required=True, domain=[('type', '=', 'sale_refund')])
    name = fields.Char(string="Motivo de Nota de Credito", required=True)
    amount = fields.Float("Monto aplicar",required=True)
    invoice_number = fields.Char("# de Factura", readonly= True)


    def _get_fecha(self, cr, uid, context=None):
        active_id = context and context.get('active_id', False)
        if active_id:
            inv = self.pool.get('account.invoice').browse(cr, uid, active_id, context=context)
            return inv.date_invoice

    def _get_amount_inv(self, cr, uid, context=None):
        active_id = context and context.get('active_id', False)
        if active_id:
            inv = self.pool.get('account.invoice').browse(cr, uid, active_id, context=context)
            return inv.residual
        else:
            return 0.00


    def _get_invoice_number(self, cr, uid, context=None):
        active_id = context and context.get('active_id', False)
        if active_id:
            inv = self.pool.get('account.invoice').browse(cr, uid, active_id, context=context)
            return inv.number
        else:
            raise except_orm(_('Advertencia'), _('.No esta validada la factura, no se puede crear notas de credito sin estar en estado Validada!!!'))

    _defaults = {
        'fecha_nota': _get_fecha,
        #'journal_id': _get_journal,
        'amount': _get_amount_inv,
        'invoice_number':_get_invoice_number,
        #'name': _get_name,
    }

    @api.one
    def invoice_nota_credito(self):
        journal_id = self.env['account.journal'].search([('type', '=', 'sale_refund')], limit=1)
        obj_refund = self.env["account.invoice"]
        inv_line_obj = self.env['account.invoice.line']
        active_id = self._context.get('active_id')
        qty = 1
        if active_id:
            inv = self.env['account.invoice'].browse(active_id)
            values = {
                'partner_id': inv.partner_id.id,
                'date_invoice': self.fecha_nota,
                'account_id': inv.account_id.id,
                'type': 'out_refund',
                'journal_id': journal_id.id,
                'origin': self.invoice_number,
                'state': 'open'
            }
            invoice_id = obj_refund.create(values)
            if invoice_id:
                vals = {
                    'name': self.name,
                    'invoice_id': invoice_id.id,
                    'account_id': journal_id.default_debit_account_id.id,
                    'price_unit': self.amount,
                    'quantity': qty,
                }
                inv_line_id = inv_line_obj.create(vals)
            if invoice_id and inv_line_id:
                new_residual = inv.residual - self.amount
                inv.write({'residual': new_residual})
        else:
            raise except_orm(_('Advertencia'), _('.No se puede crear nota de credito, consulte el administrador del sistema!!'))
