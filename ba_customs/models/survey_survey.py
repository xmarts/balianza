# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
class Survey(models.Model):
        _inherit='survey.survey'
        date_init = fields.Date(string="Fecha inicio curso")
        date_fin = fields.Date(string="Fecha fin curso")
        user_patron_id = fields.Many2one('res.users',string="Representante del patrón")
        user_facilitador_id = fields.Many2one('res.users',string="Facilitador")
        user_trabajadores_id = fields.Many2one('res.users',string="Representante de los trabajadores")
        company_id = fields.Many2one('res.company',string="Compañia relacionada")
        duration_course = fields.Integer(string="Duración del curso")
        certification_report_layout = fields.Selection([
                ('classic_red', 'Alianza'),
                ('modern_purple', 'Modern Purple'),
                ('modern_blue', 'Modern Blue'),
                ('modern_gold', 'Modern Gold'),
                ('classic_purple', 'Classic Purple'),
                ('classic_blue', 'Classic Blue'),
                ('classic_gold', 'Classic Gold')],
                string='Certification template', default='classic_red')
        