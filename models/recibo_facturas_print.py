
from openerp import api, models


class reporte(models.AbstractModel):
    _name = 'report.delivery_cost.recibo_facturas_print'

    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('delivery_cost.recibo_facturas_print')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            }
        return report_obj.render("delivery_cost.recibo_facturas_print",docargs)
      

