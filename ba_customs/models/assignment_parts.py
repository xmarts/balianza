# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError


class AssignmentParts(models.Model):
    _name = 'assignment.parts'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehículo')
    company_id = fields.Many2one('res.company',related="vehicle_id.company_id")
    product_id = fields.Many2one('product.product', string='Producto/Pieza',domain="[('type', 'in', ['product']), '|', ('company_id', '=', company_id), ('company_id', '=', False)]", required=True, check_company=True)
    product_qty = fields.Float('Cantidad',default=1.0, digits='Product Unit of Measure', required=True)
    product_uom = fields.Many2one('uom.uom', 'Unidad',readonly=True, required=True, related="product_id.uom_id")
    unit_cost = fields.Float('Costo unitario',digits='Product Unit of Measure', required=True, related="product_id.standard_price")

    @api.model_create_multi
    def create(self, values):

    	res = super(AssignmentParts, self).create(values)
    	quants = self.env['stock.quant'].search([('product_id','=',res.product_id.id)])
    	print ("Esto es quants",quants)
    	cantidad_disponible = 0
    	for quant in quants:
    		if quant.quantity > 0:
    			cantidad_disponible = cantidad_disponible + (quant.quantity - quant.reserved_quantity)

    	reservas = self.env['assignment.parts'].search([('product_id','=',res.product_id.id)])
    	cantidad_reservada = 0
    	for reserva in reservas:
    		cantidad_reservada = cantidad_reservada + (reserva.product_qty)	
    	
    	cantidad_solicitada = res.product_qty
    	print ("Esto es cantidad cantidad_solicitada",cantidad_solicitada)
    	print ("Esto es cantidad cantidad_disponible",cantidad_disponible)
    	print ("Esto es cantidad cantidad_reservada",cantidad_reservada)
    	
    	if cantidad_reservada > cantidad_disponible:
    		raise ValidationError("Para el producto: " + str(res.product_id.name) + " no hay cantidad suficiente disponible en almacen para asignación de complemento o se encuentra asignado en otro vehiculo.")
    	return res

    def write(self, values):
    	res = super(AssignmentParts, self).write(values)
    	quants = self.env['stock.quant'].search([('product_id','=',self.product_id.id)])
    	print ("Esto es quants",quants)
    	cantidad_disponible = 0
    	for quant in quants:
    		if quant.quantity > 0:
    			cantidad_disponible = cantidad_disponible + (quant.quantity - quant.reserved_quantity)

    	reservas = self.env['assignment.parts'].search([('product_id','=',self.product_id.id)])
    	cantidad_reservada = 0
    	for reserva in reservas:
    		cantidad_reservada = cantidad_reservada + (reserva.product_qty)	
    	cantidad_solicitada = self.product_qty
    	print ("Esto es cantidad cantidad_solicitada",cantidad_solicitada)
    	print ("Esto es cantidad cantidad_disponible",cantidad_disponible)
    	print ("Esto es cantidad cantidad_reservada",cantidad_reservada)
    	if cantidad_reservada > cantidad_disponible:
    		raise ValidationError("Para el producto: " + str(self.product_id.name) + " no hay cantidad suficiente disponible en almacen para asignación de complemento o se encuentra asignado en otro vehiculo.")
    	return res
