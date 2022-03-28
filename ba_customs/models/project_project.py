# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import datetime
from lxml import etree

class ProjectProject(models.Model):

	_inherit = 'project.project'

	ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket de servicio relacionado:")