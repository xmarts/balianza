# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ResUsers(models.Model):
    _inherit = 'res.users'

    nombramiento_elearning = fields.Char(string="Titulo")
    firma_digital = fields.Binary(string="Firma digital")
    karma = fields.Integer('Karma', default=10)