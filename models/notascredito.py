# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
class Notascredito(models.Model):
    _inherit = "account.invoice"

    @api.one
    def invoice_cancel_veddepessa(self):
        for inv in self:
            inv.write({'state': 'open'})


