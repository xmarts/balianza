# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_driver = fields.Boolean(string="Es chofer interno?")

    @api.model
    def create(self, vals):
    	res = super(ResPartner, self).create(vals)
    	if self.env.context.get('is_driver'):
    		res.is_driver = True
    	return res