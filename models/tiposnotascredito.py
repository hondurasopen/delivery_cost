# -*- encoding: utf-8 -*-
from openerp import fields, models, exceptions, api, _
import base64
import csv
import cStringIO
from openerp.exceptions import except_orm, Warning, RedirectWarning


class TiposNotacredito(models.Model):
    _name = "tipo.nota.debito.factura"

    name = fields.Char("Tipo de Nota")
    cuenta = fields.Many2one("account.account", "Cuenta", domain="[('type','not in',['view'])]", required=True)
    notas = fields.Text("Observaciones")
    desc_nota = fields.Char("Descripción")


