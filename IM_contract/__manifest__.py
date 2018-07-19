# Copyright 2018 Comunitea - Santi Argüeso
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Improving Metrics recurrent invoicing',
    'version': '11.0.1.0.0',
    'category': 'Contract Management',
    'license': 'AGPL-3',
    'author': "Comunitea,",
    'website': 'https://www.comunitea.com',
    'depends': [
        'contract_variable_quantity',
        'jira_connector'
    ],
    'data': [
        'views/contract_view.xml',
    ],
    'installable': True,
}
