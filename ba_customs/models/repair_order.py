# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import datetime
from odoo.tools import float_compare

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo')
    product_id = fields.Many2one('product.product', string='Product to Repair', domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', company_id), ('company_id', '=', False)]", readonly=True, required=False, states={'draft': [('readonly', False)]}, check_company=True)
    product_uom = fields.Many2one('uom.uom', 'Product Unit of Measure', readonly=True, required=False, states={'draft': [('readonly', False)]}, domain="[('category_id', '=', product_uom_category_id)]")

    def action_validate(self):
        print ("Esto es context",self.env.context)
        if self.env.context.get('vehicle_id') or self.vehicle_id != False:
            for line in self.operations:
                quants = self.env['stock.quant'].search([('product_id','=',line.product_id.id),('location_id','=',line.location_id.id)])
                cantidad_disponible = 0
                for quant in quants:

                    cantidad_disponible = cantidad_disponible + (quant.quantity - quant.reserved_quantity)
                cantidad_solicitada = line.product_uom_qty
                if cantidad_solicitada > cantidad_disponible:
                    raise UserError(_("Para el producto a utilizar: "+str(line.product_id.name)+" no se encontró cantidad suficiente disponible en el almacen: " +str(line.location_id.name)))
            self.action_repair_confirm()
        else:
            self.ensure_one()
            if self.filtered(lambda repair: any(op.product_uom_qty < 0 for op in repair.operations)):
                raise UserError(_("No puede ingresar cantidades negativas."))
            if self.product_id.type == 'consu':
                return self.action_repair_confirm()
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            available_qty_owner = self.env['stock.quant']._get_available_quantity(self.product_id, self.location_id, self.lot_id, owner_id=self.partner_id, strict=True)
            available_qty_noown = self.env['stock.quant']._get_available_quantity(self.product_id, self.location_id, self.lot_id, strict=True)
            repair_qty = self.product_uom._compute_quantity(self.product_qty, self.product_id.uom_id)
            for available_qty in [available_qty_owner, available_qty_noown]:
                if float_compare(available_qty, repair_qty, precision_digits=precision) >= 0:
                    return self.action_repair_confirm()
            else:
                return {
                    'name': self.product_id.display_name + _(': Insufficient Quantity To Repair'),
                    'view_mode': 'form',
                    'res_model': 'stock.warn.insufficient.qty.repair',
                    'view_id': self.env.ref('repair.stock_warn_insufficient_qty_repair_form_view').id,
                    'type': 'ir.actions.act_window',
                    'context': {
                        'default_product_id': self.product_id.id,
                        'default_location_id': self.location_id.id,
                        'default_repair_id': self.id,
                        'default_quantity': repair_qty,
                        'default_product_uom_name': self.product_id.uom_name
                    },
                    'target': 'new'
                }

    def action_repair_done(self):
        if self.filtered(lambda repair: not repair.repaired):
            raise UserError(_("Repair must be repaired in order to make the product moves."))
        self._check_company()
        self.operations._check_company()
        self.fees_lines._check_company()
        res = {}
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        Move = self.env['stock.move']

        if self.env.context.get('vehicle_id') or self.vehicle_id.id != False:
            print ("Ingresa a la modificación esto es el contexto",self.env.context)
            for repair in self:
                moves = self.env['stock.move']
                for operation in repair.operations:
                    move = Move.create({
                        'name': repair.name,
                        'product_id': operation.product_id.id,
                        'product_uom_qty': operation.product_uom_qty,
                        'product_uom': operation.product_uom.id,
                        'partner_id': repair.address_id.id,
                        'location_id': operation.location_id.id,
                        'location_dest_id': operation.location_dest_id.id,
                        'repair_id': repair.id,
                        'origin': repair.name,
                        'company_id': repair.company_id.id,
                    })

                    product_qty = move.product_uom._compute_quantity(
                        operation.product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')

                    available_quantity = self.env['stock.quant']._get_available_quantity(
                        move.product_id,
                        move.location_id,
                        lot_id=operation.lot_id,
                        strict=False,
                    )
                    move._update_reserved_quantity(
                        product_qty,
                        available_quantity,
                        move.location_id,
                        lot_id=operation.lot_id,
                        strict=False,
                    )

                    move._set_quantity_done(operation.product_uom_qty)

                    if operation.lot_id:
                        move.move_line_ids.lot_id = operation.lot_id

                    moves |= move
                    moves._action_done()
                    operation.write({'move_id': move.id, 'state': 'done'})
                res[repair.id] = move.id
            return res
        else:
            for repair in self:
                owner_id = False
                available_qty_owner = self.env['stock.quant']._get_available_quantity(repair.product_id, repair.location_id, repair.lot_id, owner_id=repair.partner_id, strict=True)
                if float_compare(available_qty_owner, repair.product_qty, precision_digits=precision) >= 0:
                    owner_id = repair.partner_id.id

                moves = self.env['stock.move']
                for operation in repair.operations:
                    move = Move.create({
                        'name': repair.name,
                        'product_id': operation.product_id.id,
                        'product_uom_qty': operation.product_uom_qty,
                        'product_uom': operation.product_uom.id,
                        'partner_id': repair.address_id.id,
                        'location_id': operation.location_id.id,
                        'location_dest_id': operation.location_dest_id.id,
                        'repair_id': repair.id,
                        'origin': repair.name,
                        'company_id': repair.company_id.id,
                    })

                    product_qty = move.product_uom._compute_quantity(
                        operation.product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')

                    available_quantity = self.env['stock.quant']._get_available_quantity(
                        move.product_id,
                        move.location_id,
                        lot_id=operation.lot_id,
                        strict=False,
                    )
                    move._update_reserved_quantity(
                        product_qty,
                        available_quantity,
                        move.location_id,
                        lot_id=operation.lot_id,
                        strict=False,
                    )

                    move._set_quantity_done(operation.product_uom_qty)

                    if operation.lot_id:
                        move.move_line_ids.lot_id = operation.lot_id

                    moves |= move
                    operation.write({'move_id': move.id, 'state': 'done'})
                move = Move.create({
                    'name': repair.name,
                    'product_id': repair.product_id.id,
                    'product_uom': repair.product_uom.id or repair.product_id.uom_id.id,
                    'product_uom_qty': repair.product_qty,
                    'partner_id': repair.address_id.id,
                    'location_id': repair.location_id.id,
                    'location_dest_id': repair.location_id.id,
                    'move_line_ids': [(0, 0, {'product_id': repair.product_id.id,
                    'lot_id': repair.lot_id.id,
                    'product_uom_qty': 0,  # bypass reservation here
                    'product_uom_id': repair.product_uom.id or repair.product_id.uom_id.id,
                    'qty_done': repair.product_qty,
                    'package_id': False,
                    'result_package_id': False,
                    'owner_id': owner_id,
                    'location_id': repair.location_id.id, #TODO: owner stuff
                    'company_id': repair.company_id.id,
                    'location_dest_id': repair.location_id.id,})],
                    'repair_id': repair.id,
                    'origin': repair.name,
                    'company_id': repair.company_id.id,
                })
                consumed_lines = moves.mapped('move_line_ids')
                produced_lines = move.move_line_ids
                moves |= move
                moves._action_done()
                produced_lines.write({'consume_line_ids': [(6, 0, consumed_lines.ids)]})
                res[repair.id] = move.id
            return res

class RepairLine(models.Model):
    _inherit = 'repair.line'

    
