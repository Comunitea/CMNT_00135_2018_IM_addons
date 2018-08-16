# -*- coding: utf-8 -*-
# © 2018 Comunitea - Javier Colmenero <javier@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'IM Custom Documents',
    'version': '11.0.1.0.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "Comunitea,",
    'website': 'https://www.comunitea.com',
    'depends': [
        'base',
        'web',
        'account_due_dates_str',
        'IM_contract'
    ],
    'data': [
        'views/ir_qweb.xml',
        'views/report_invoice.xml',
    ],
    'installable': True,
}
