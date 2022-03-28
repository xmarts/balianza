# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2021-Present Bodegas Alianza - Jose Luigi Tolayo
#     (<>).
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Bodegas Alianza Sincronización',
    'version': '1.0',
    'depends': [
            'base',
            'website',
            'survey',
            'website_slides',
            'website_slides_survey',
            'website_helpdesk_form',
            'repair',
            'stock',
            'point_of_sale',
            'hr_fleet',
            'fleet',
            'project'
    ],
    'license': 'Other proprietary',
    'price': 9999.0,
    'category': 'Sales',
    'currency': 'MXN',
    'summary': """Bodegas Alianza Custom module""",
    'description': "",
    'author': 'José Luigi Tolayo Osorio',
    'support': 'luigi.tolayo@bodegasalianza.com',
    'images': [],

    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/survey_survey_view.xml',
        'views/res_users_view.xml',
        'views/slides_templates_view.xml',
        'views/http_routing_template.xml',
        'views/res_partner_view.xml',
        'views/employee_view.xml',
        'views/repair_order_view.xml',
        'views/product_template_view.xml',
        'views/fleet_vehicle_view.xml',
        'views/helpdesk_ticket_view.xml',
        'views/project_project_view.xml'
        
    ],
    'installable': True,
    'application': False,
}


