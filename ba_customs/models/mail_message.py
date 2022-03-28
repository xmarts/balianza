# -*- coding: utf-8 -*-
import logging
import re
from binascii import Error as binascii_error
from collections import defaultdict
from operator import itemgetter
from odoo import _, api, fields, models, modules, tools
from odoo.exceptions import AccessError, UserError
from odoo.http import request
from odoo.osv import expression
from odoo.tools import groupby

_logger = logging.getLogger(__name__)
_image_dataurl = re.compile(r'(data:image/[a-z]+?);base64,([a-z0-9+/\n]{3,}=*)\n*([\'"])(?: data-filename="([^"]*)")?', re.I)

class Message(models.Model):
	_inherit = 'mail.message'

	@api.model_create_multi
	def create(self, values_list):
		print ("Ingresa al new create de mail.message",values_list)
		tracking_values_list = []
		for values in values_list:
			#Modificación By Luigi Tolayo forzar que tome como email_from el correo de servidor saliente
			registros = self.env['ir.mail_server'].sudo().search([])
			if len(registros) == 1:
				for saliente in registros:
					if values['email_from'] != saliente.sudo().smtp_user:
						values['email_from'] = saliente.sudo().smtp_user
		
			if 'email_from' not in values:  # needed to compute reply_to
				print ("Ingresa cuando no encuentra email_from",values)
				author_id, email_from = self.env['mail.thread']._message_compute_author(values.get('author_id'), email_from=None, raise_exception=False)
				values['email_from'] = email_from
			if not values.get('message_id'):
				values['message_id'] = self._get_message_id(values)
			if 'reply_to' not in values:
				values['reply_to'] = self._get_reply_to(values)
			if 'record_name' not in values and 'default_record_name' not in self.env.context:
				values['record_name'] = self._get_record_name(values)

			if 'attachment_ids' not in values:
				values['attachment_ids'] = []
			# extract base64 images
			if 'body' in values:
				Attachments = self.env['ir.attachment']
				data_to_url = {}
				def base64_to_boundary(match):
					key = match.group(2)
					if not data_to_url.get(key):
						name = match.group(4) if match.group(4) else 'image%s' % len(data_to_url)
						try:
							attachment = Attachments.create({
								'name': name,
								'datas': match.group(2),
								'res_model': values.get('model'),
								'res_id': values.get('res_id'),
							})
						except binascii_error:
							_logger.warning("Impossible to create an attachment out of badly formated base64 embedded image. Image has been removed.")
							return match.group(3)  # group(3) is the url ending single/double quote matched by the regexp
						else:
							attachment.generate_access_token()
							values['attachment_ids'].append((4, attachment.id))
							data_to_url[key] = ['/web/image/%s?access_token=%s' % (attachment.id, attachment.access_token), name]
					return '%s%s alt="%s"' % (data_to_url[key][0], match.group(3), data_to_url[key][1])
				values['body'] = _image_dataurl.sub(base64_to_boundary, tools.ustr(values['body']))
			# delegate creation of tracking after the create as sudo to avoid access rights issues
			tracking_values_list.append(values.pop('tracking_value_ids', False))

		messages = super(Message, self).create(values_list)

		check_attachment_access = []
		if all(isinstance(command, int) or command[0] in (4, 6) for values in values_list for command in values.get('attachment_ids')):
			for values in values_list:
				for command in values.get('attachment_ids'):
					if isinstance(command, int):
						check_attachment_access += [command]
					elif command[0] == 6:
						check_attachment_access += command[2]
					else:  # command[0] == 4:
						check_attachment_access += [command[1]]

		else:
			check_attachment_access = messages.mapped('attachment_ids').ids  # fallback on read if any unknow command
		if check_attachment_access:
			self.env['ir.attachment'].browse(check_attachment_access).check(mode='read')

		for message, values, tracking_values_cmd in zip(messages, values_list, tracking_values_list):
			if tracking_values_cmd:
				vals_lst = [dict(cmd[2], mail_message_id=message.id) for cmd in tracking_values_cmd if len(cmd) == 3 and cmd[0] == 0]
				other_cmd = [cmd for cmd in tracking_values_cmd if len(cmd) != 3 or cmd[0] != 0]
				if vals_lst:
					self.env['mail.tracking.value'].sudo().create(vals_lst)
				if other_cmd:
					message.sudo().write({'tracking_value_ids': tracking_values_cmd})
			if message.is_thread_message(values):
				message._invalidate_documents(values.get('model'), values.get('res_id'))
		return messages