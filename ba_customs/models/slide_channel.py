# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import json
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class SlideChannelInvite(models.TransientModel):
    _inherit = 'slide.channel.invite'


    @api.model
    def create(self, values):
        values['channel_id'] = self.env.context.get('active_id')
        return super(SlideChannelInvite, self).create(values)

    @api.depends('template_id')
    def _compute_subject(self):
        for invite in self:
            bodies = self.env['mail.template']._render_template(invite.template_id.subject, invite.template_id.model,self.env.context.get('active_ids') , post_process=True)
            data = str(bodies)[5:-2].replace('\\n', '')
            if invite.template_id:
                invite.subject = data
            elif not invite.subject:
                invite.subject = False

    @api.depends('template_id')
    def _compute_body(self):
        for invite in self:
            bodies = self.env['mail.template']._render_template(invite.template_id.body_html, invite.template_id.model,self.env.context.get('active_ids') , post_process=True)
            data = str(bodies)[5:-2].replace('\\n', '')
            if invite.template_id:
                invite.body = data
            elif not invite.body:
                invite.body = False

class Channel(models.Model):
    _inherit = 'slide.channel'
    
    def action_channel_invite(self):

        self.ensure_one()
        template = self.env.ref('website_slides.mail_template_slide_channel_invite', raise_if_not_found=False)
        ctx = {
            'default_model': 'slide.channel',
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'mark_so_as_sent': True,
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'slide.channel.invite',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
