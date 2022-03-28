# -*- coding: utf-8 -*-
from itertools import islice
from xml.etree import ElementTree as ET

import odoo

from odoo import http, models, fields, _
from odoo.http import request
from odoo.addons.website.controllers.main import Website

class Website_ba(Website):
	def _login_redirect(self, uid, redirect=None):
		if not redirect and request.params.get('login_success'):
			if request.env['res.users'].browse(uid).has_group('base.group_user'):
				redirect = b'/web?' + request.httprequest.query_string
			else:
				redirect = '/slides'
		return super()._login_redirect(uid, redirect=redirect)