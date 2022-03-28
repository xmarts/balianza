# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import datetime
from lxml import etree

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    punto_de_venta = fields.Many2one('pos.config', string="Centro de trabajo")
    task_related_id = fields.Many2one('project.task', string="Tarea relacionada")
    tag_ids = fields.Many2one('helpdesk.tag', string="Sub categorías")
    tag_ba_ids = fields.Many2one('helpdesk.tag.ba')


class HelpdeskTag(models.Model):
    _inherit = 'helpdesk.tag'

    team_id = fields.Many2one('helpdesk.team', string="Equipo de mesa de servicio")

class HelpdeskTagBa(models.Model):
    _name = 'helpdesk.tag.ba'

    name = fields.Char(string="Sub categoria")
    tag_id = fields.Many2one('helpdesk.tag', string="Categoria padre")

    def name_get(self):
    	return [(tag_ba.id, '%s/%s' % (tag_ba.tag_id.name,tag_ba.name)) for tag_ba in self]


class HelpdeskTeam(models.Model):

	_inherit = 'helpdesk.team'

	name = fields.Char(string="Equipo mesa de servicio", required = "True")
	website_form_view_id = fields.Many2one('ir.ui.view', string="Form", copy="False")
	project_related_id = fields.Many2one('project.project', string="Proyecto relacionado")

	"""def _ensure_submit_form_view(self):
		for team in self:
			if not team.website_form_view_id:
				default_form = etree.fromstring(self.env.ref('ba_customs.ticket_submit_form_ba').arch)
				xmlid = 'website_helpdesk_form.team_form_' + str(team.id)
				form_template = self.env['ir.ui.view'].create({
					'type': 'qweb',
					'arch': etree.tostring(default_form),
					'name': xmlid,
					'key': xmlid
				})

				self.env['ir.model.data'].create({
					'module': 'website_helpdesk_form',
					'name': xmlid.split('.')[1],
					'model': 'ir.ui.view',
					'res_id': form_template.id,
					'noupdate': True
				})

				team.write({'website_form_view_id': form_template.id})"""
		