# -*- coding: utf-8 -*-
# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api
from odoo.tools import html_escape as escape


class IrQwebFieldContact(models.AbstractModel):

    _inherit = 'ir.qweb.field.contact'

    @api.model
    def value_to_html(self, value, options):
        if not value.exists():
            return False

        opf = options and options.get('fields') or ["name", "address", "phone", "mobile", "email"]
        val = super(IrQwebFieldContact, self).value_to_html(value, options)
        value = value.sudo().with_context(show_address=True)
        name_get = value.name_get()[0][1]
        val = {
            'name': name_get.split("\n")[0],
            'address': escape("\n".join(name_get.split("\n")[1:])).strip(),
            'phone': value.phone,
            'mobile': value.mobile,
            'city': value.city,
            'country_id': value.country_id.display_name,
            'website': value.website,
            'email': value.email,
            'fields': opf,
            'object': value,
            'options': options,
            'vat': value.vat
        }
        return self.env['ir.qweb'].render('base.contact', val)
