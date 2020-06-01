# -*- encoding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class Salefleet(models.Model):
    _inherit = 'sale.order'

    @api.one
    def gettotal_fleet(self):
        sum_fleet = 0
        for order in self:
            for line in order.sale_line_fleet_ids:
                sum_fleet += line.total
        self.total_flete = sum_fleet

    @api.one
    def computetotalcosto(self):
        sum_line = 0
        for line in self.order_line:
            sum_line += line.purchase_price
        self.costo_producto = sum_line

    pedido_incidente = fields.Boolean("Flete con incidente")
    registro_flete = fields.Boolean("Incidente registrado")
    costo_producto = fields.Float("Costo Combustible", compute='computetotalcosto')
    sale_line_fleet_ids = fields.One2many("sale.order.line.delivery", "sale_id", "Fletes")
    total_fleet = fields.Float("Total de Flete")
    transportista_id = fields.Many2one("res.partner", "Transportista", domain=[('transportista','=',True)], required=True)
    invoice_id = fields.Many2one("account.invoice", "Factura de Flete", readonly=True)
    total_flete = fields.Float("Total del Flete", compute='gettotal_fleet')
    optional_address = fields.Text("Dirección de Factura", help="Si existe direeción de facturación, esta sera la dirección que se mostrara en la factura")
    nota_incidentes = fields.Text("Incidente de flete")
    purchase_id = fields.Many2one("purchase.order", "Orden de Compra")
    proveedor_combustible_id = fields.Many2one("res.partner", "Proveedor", domain=[('supplier','=',True),('transportista','=',False)], required=True)
    hora_entrada = fields.Datetime("Fecha y hora de entrada")
    hora_salida = fields.Datetime("Fecha y hora de salida")

    # Funcion overridden para fecha de factura
    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        values = super(Salefleet, self)._prepare_invoice(cr, uid, order, lines, context=context)
        values['date_invoice'] = order.date_order
        values['optional_address'] = order.optional_address
        return values

    # Funcion para Confirmar pedido de ventas
    def action_button_confirm(self, cr, uid, ids, context=None):
        inh = super(Salefleet, self).action_button_confirm(cr, uid, ids, context=context)
        delivery_cost_obj = self.pool.get("sale.order.line.delivery")
        vals = {}
        self.create_purchase(cr, uid, ids, context=None)
        for order in self.browse(cr, uid, ids, context=context):
            for line in order.order_line:
                vals = {
                    'date': order.date_order,
                    'sale_id': order.id,
                    'transportista_id': order.transportista_id.id,
                    'product_id': line.product_id.id,
                    'qty_galones': line.product_uom_qty,
                    'unidad_medida': line.product_uom.id,
                    'hora_entrada': order.hora_entrada,
                    'hora_salida': order.hora_salida,
                }
                delivery_cost_obj.create(cr, uid, vals, context)
        return inh

    def create_purchase(self, cr, uid, ids, context=None):
        purchase_obj = self.pool.get('purchase.order')
        purchase_line_obj = self.pool.get('purchase.order.line')
        values = {}
        vals = {}
        purchase_validate = False
        purchase_id = 0
        for order in self.browse(cr, uid, ids, context=context):
            for line in order.order_line:
                if order.purchase_id:
                    order.purchase_id.unlink()

                if not purchase_validate:
                    type_obj = self.pool.get('stock.picking.type')
                    # TODO: Hacer un OR en el dominio de pickin
                    picking = type_obj.browse(cr, uid, type_obj.search(cr, uid, [('code', '=', 'incoming'), ('name', '=', 'Dropship')], context=context, limit=1), context=context)
                    location = self.pool.get("stock.picking.type").browse(cr, uid, picking.id, context=context)
                    #pricelist = self.pool.get('res.partner').browse(cr, uid, [('id', '=', line.product_id.seller_ids.name.id)], context=context).property_product_pricelist_purchase.id
                    vals = {
                        'partner_id': order.proveedor_combustible_id.id,
                        'date_order': order.date_order,
                        'origin': order.name,
                        'picking_type_id': picking.id,
                        'location_id': location.default_location_dest_id.id,
                        'invoice_method': 'order',
                        'dest_address_id': order.partner_id.id, 
                        'pricelist_id': line.product_id.seller_ids.name.property_product_pricelist_purchase.id,
                    }

                    purchase_id = purchase_obj.create(cr, uid, vals, context)
                    if purchase_id:
                        purchase_validate = True

                if purchase_id:
                    #acc_id = self._choose_account_from_dilvery_line(line)
                    values = {
                        'name': line.name,
                        'order_id': purchase_id,
                        'date_planned': order.date_order,
                        #'account_id': acc_id,
                        'price_unit': line.purchase_price or 0.0,
                        'product_qty': line.product_uom_qty,
                        'product_id': line.product_id.id or False,
                        # 'uos_id': False,
                    }
                    purchase_line_id = purchase_line_obj.create(cr, uid, values, context)

            if purchase_id:
                self.write(cr, uid, ids, {'purchase_id': purchase_id}, context=context)
        #return True

    def _choose_account_from_dilvery_line(self, line):
        property_obj = self.pool.get('ir.property')
        if line.product_id:
            acc_id = line.product_id.property_account_expense.id
            if not acc_id:
                acc_id = line.product_id.categ_id.property_account_expense_categ.id
            if not acc_id:
                raise except_orm(_('Error!'), _('Define an expense account for this product: "%s" (id:%d).') % (line.product_id.name,line.product_id.id,))
        else:
            acc_id = property_obj.get('property_account_expense_categ', 'product.category').id
        return acc_id


    # revisa cuenta en producto para verificar la creación de la factura de flete
    def _choose_account_from_dilvery_line(self, line):
        property_obj = self.pool.get('ir.property')
        if line.product_id:
            acc_id = line.product_id.property_account_expense.id
            if not acc_id:
                acc_id = line.product_id.categ_id.property_account_expense_categ.id
            if not acc_id:
                raise except_orm(_('Error!'), _('Define an expense account for this product: "%s" (id:%d).') % (line.product_id.name,line.product_id.id,))
        else:
            acc_id = property_obj.get('property_account_expense_categ', 'product.category').id
        return acc_id

    # Crea Factura de Flete para transportista
    @api.multi
    def create_invoice(self):
        delivery_line_obj = self.env["sale.order.line.delivery"]
        inv_obj = self.env['account.invoice']
        inv_line_obj = self.env['account.invoice.line']
        values = {}
        vals = {}
        journal_id = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1).id
        partner_id = 0
        invoice_id = 0
        sum_fleet = 0
        for order in self:
            for line in order.sale_line_fleet_ids:
                sum_fleet += line.total
                if line.invoice_fleet_id.id:
                    inv_obj.search([('id', '=', line.invoice_fleet_id.id)]).unlink()
                    partner_id = 0

                if partner_id != line.transportista_id.id:
                    values = {
                        'partner_id': line.transportista_id.id,
                        'date_invoice': order.date_order,
                        'account_id': line.transportista_id.property_account_payable.id,
                        'type': 'in_invoice',
                        'journal_id': journal_id,
                        'origin':order.name
                        }
                    partner_id = line.transportista_id.id
                    invoice_id = inv_obj.create(values)
                #Condicion para crear le objeto linea de factura account.invoice.line

                if invoice_id:
                    acc_id = self._choose_account_from_dilvery_line(line)
                    vals = {
                        'name': line.description,
                        'invoice_id': invoice_id.id,
                        'account_id': acc_id,
                        'price_unit': line.costo_galon or 0.0,
                        'quantity': line.qty_galones,
                        'product_id': line.product_id.id or False,
                        'uos_id': line.unidad_medida.id or False,
                    }
                    line.write({'invoice_fleet_id': invoice_id.id})
                    line.write({'state': 'open'})
                    inv_line_id = inv_line_obj.create(vals)

            self.total_flete = sum_fleet
            if invoice_id:
                order.write({'invoice_id': invoice_id.id})

        return True

    @api.one
    def registrar_incidente(self):
        if self.pedido_incidente:
            for line in self.sale_line_fleet_ids:
                line.write({'flete_incidente': True})
                line.write({'nota_incidentes': self.nota_incidentes})
                line.hora_entrada = self.hora_entrada,
                line.hora_salida = self.hora_salida,
                self.registro_flete = True


class Salefleetline(models.Model):
    _name = "sale.order.line.delivery"
    _order = "sale_id asc"

    @api.one
    def getstatusinvoice(self):
        if self.invoice_fleet_id.id:
            if self.invoice_fleet_id.state == 'paid':
                self.write({'state': 'paid'})
                self.paid_state = True

    sale_id = fields.Many2one("sale.order", "# Orden de Venta")
    partner_id = fields.Many2one("res.partner", "Cliente", related="sale_id.partner_id")
    invoice_fleet_id = fields.Many2one("account.invoice", string="Factura de Flete")
    factura_cliente_id = fields.Many2many("account.invoice", "# Factura", related="sale_id.invoice_ids", limit=1)
    transportista_id = fields.Many2one("res.partner", "Transportista", domain=[('transportista', '=', True)], required=True)
    fletes_id = fields.Many2one("delivery.cost.fleet", "Destino")
    origin_id = fields.Many2one("delivery.port.origin", "Puerto de Origen")
    name = fields.Many2one("delivery.transportista.unidades", "No. de Pipa")
    numero_placa = fields.Char("No. Placa", related="name.numero_placa")
    description = fields.Char("Descripcion", default="Flete de Combustible", required=True)
    qty_galones = fields.Float("Cant. de Gals")
    costo_galon = fields.Float("Costo por Galón")
    unidad_medida = fields.Many2one('product.uom', string='Unit of Measure', ondelete='set null', index=True)
    total = fields.Float("Total")
    product_id = fields.Many2one("product.product", "Producto", required=True)
    date = fields.Date("Fecha del Flete")
    state = fields.Selection([
            ('draft', 'Borrador'),
            ('open', 'Pendiente de Liquidar'),
            ('paid', 'Pagado'),
        ], string='Estado', index=True, default='draft', help="")
    paid_state = fields.Boolean(compute=getstatusinvoice, default=False, string="Flete Pagado")
    flete_incidente = fields.Boolean("Flete con incidente")
    conductor = fields.Char("Conductor")
    nota_incidentes = fields.Text("Incidente")
    chofer_id = fields.Many2one("delivery.chofer", "Chofer")
    deposito = fields.Many2one("delivery.transportista.unidades.depositos", "Depósito")
    sellos_valvulas = fields.Char("Sellos Valvula")
    sellos_manhole = fields.Char("Sellos Manhole")
    api_cliente = fields.Char("API")
    hora_entrada = fields.Datetime("Fecha y hora de entrada")
    hora_salida = fields.Datetime("Fecha y hora de salida")

    @api.multi
    @api.depends("sale_id", "sale_id.order_line")
    @api.onchange("fletes_id")
    def _onchangeproduct(self):
        #order_obj = self.env["sale.order"].browse(active_id)
        vals = []
        vals1 = []
        for order_line in self.sale_id.order_line:
            vals.append(order_line.product_id.id)
        # self.origin_id=self.fletes_id.origin_id.id
        #return {'domain': {'product_id': [('id', 'in', vals)]}}

    @api.onchange("fletes_id")
    def _onchangecosto(self):
        self.costo_galon = self.fletes_id.costo_galon
        if self.qty_galones > 0:
            self.total = self.qty_galones * self.costo_galon

    @api.onchange("qty_galones")
    def _onchangetotalqty(self):
        if self.qty_galones > 0:
            self.total = self.qty_galones * self.costo_galon

    @api.onchange("costo_galon")
    def _onchangetotalcost(self):
        if self.qty_galones > 0:
            self.total = self.qty_galones * self.costo_galon

