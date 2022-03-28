# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import datetime

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    repair_count = fields.Integer(compute="_compute_count_repair", string='Contract Count')
    assignment_parts_ids = fields.One2many('assignment.parts', 'vehicle_id', string="Asignación de complementos")

    @api.onchange('assignment_parts_ids')
    def onchange_assignment_parts_ids(self):
        product = []
        for register in self.assignment_parts_ids:
            if register.product_id in product:
                raise ValidationError("El producto: " + str(register.product_id.name) + " ya se encuentra agregado al pedido.")
            else:
                product.append(register.product_id)

    def _compute_count_repair(self):
        repair = self.env['repair.order']
        for record in self:
            record.repair_count = repair.search_count([('vehicle_id', '=', record.id)])

    def return_action_to_open_repair(self):
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window']._for_xml_id('ba_customs.%s' % xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('vehicle_id', '=', self.id)]
                )
            return res
        return False

class FleetVehicleOdometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    driver_id = fields.Many2one('res.partner', string="Driver", readonly=False, related=False)
    date = fields.Date(default=fields.Date.context_today, required=True)
    

    @api.model
    def create(self, vals):
    	res = super(FleetVehicleOdometer, self).create(vals)
    	ultimo_odometro = self.env['fleet.vehicle.odometer'].search([('vehicle_id','=',self.vehicle_id.id)],order="value desc",limit=1).value
    	ultima_fecha = self.env['fleet.vehicle.odometer'].search([('vehicle_id','=',res.vehicle_id.id)],order="date desc",limit=2)
    	for ultima in ultima_fecha:
    		if ultima.date > res.date:
    			raise ValidationError(_('La fecha ingresada debe ser mayor o igual a las fechas registradas anteriormente'))
    			

    	if ultimo_odometro >= res.value:
    		raise ValidationError(_('El valor del odometro capturado no puede ser menor o igual al ultimo registrado en el vehiculo.'))
    	return res


    @api.onchange('value')
    def _onchange_value(self):
    	if self.value:
	    	if self.vehicle_id:
	    		ultimo_odometro = self.env['fleet.vehicle.odometer'].search([('vehicle_id','=',self.vehicle_id.id)],order="value desc",limit=1).value
	    		if ultimo_odometro >= self.value:
	    			 raise ValidationError(_('El valor del odometro capturado no puede ser menor o igual al ultimo registrado en el vehiculo.'))
	    	else:
	    		raise ValidationError(_('Primero debe seleccionar el vehiculo'))