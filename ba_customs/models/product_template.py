# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import datetime

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    vehicle_complement = fields.Boolean(string="Uso en flotilla")

    @api.model
    def create(self, vals):
    	res = super(ProductTemplate, self).create(vals)
    	if self.env.context.get('vehicle_complement'):
    		res.vehicle_complement = True
    		res.sale_ok = False
    	return res