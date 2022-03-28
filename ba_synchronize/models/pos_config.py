# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
#Añadido para complementar integración SIA-ODOO en puntos de venta.
class PosConfig(models.Model):

	_inherit='pos.config'

	code = fields.Char(string="Codigo punto de venta") 
	liga = fields.Char(string="Liga")
	status = fields.Boolean(string="Estatus")
	database = fields.Char(string="Base")
	
	def name_get(self):
		result = []
		for config in self:
			result.append((config.id, "%s (%s)" % (config.code,config.name)))
		return result
	#pendiente
	@api.constrains('company_id', 'invoice_journal_id')
	def _check_company_invoice_journal(self):
		if self.invoice_journal_id and self.invoice_journal_id.company_id.id != self.company_id.id:
			print("Pasa en _check_company_invoice_journal")
