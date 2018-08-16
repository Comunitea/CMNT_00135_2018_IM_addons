# Copyright 2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models, exceptions
from odoo.tools import float_is_zero
from odoo.tools.safe_eval import safe_eval


class AccountAnalyticAccountComponent(models.Model):
    _name = "account.analytic.account.component"

    component_ids = fields.Many2many(
        comodel_name='jira.project.component',
        string='Component',
    )
    common_percent_impl = fields.Float("Implementation Percent",
                                      help="Implementation percent for "
                                           "common components")
    common_percent_maint = fields.Float("Maintaining Percent",
                                       help="Maintaining percent for "
                                            "common components")
    account_id = fields.Many2one(
            'account.analytic.account',
            string='Contract',
        )

class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    by_component = fields.Boolean(
        string='Invoice by component',
        help="If checked, contract create one invoice by component",
    )
    invoice_component_ids = fields.One2many(
        string="Components to invoice",
        comodel_name='account.analytic.account.component',
        inverse_name='account_id')
    common_component_ids = fields.Many2many(
        string="Common Components to invoice",
        comodel_name='jira.project.component')
    report_description = fields.Html('Report Description', 
                                     default='', sanitize_style=True, 
                                     strip_classes=True)

    @api.multi
    def _create_invoice(self):
        self.ensure_one()
        if self.by_component:
            invoices = self.env['account.invoice']
            ctx = self.env.context.copy()
            for component in self.invoice_component_ids:
                ctx.update({
                    'component': component,
                })
                invoices |= super(AccountAnalyticAccount, self.with_context(
                    ctx))._create_invoice()
            return invoices
        else:
            return super(AccountAnalyticAccount, self)._create_invoice()

    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        if not self._context.get('component'):
            return super(AccountAnalyticAccount, self)._prepare_invoice()
        else:
            component = self._context.get('component')
            res = super(AccountAnalyticAccount, self)._prepare_invoice()
            reference = res.get('reference', ) or ""
            reference += " (" + component.component_ids[0].name +")"
            res['reference'] = reference

            return res


    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        vals = super(AccountAnalyticAccount, self)._prepare_invoice_line(
            line, invoice_id)
        if line.qty_type == 'component':
            eval_context = {
                'env': self.env,
                'context': self.env.context,
                'user': self.env.user,
                'line': line,
                'contract': line.analytic_account_id,
                'invoice': self.env['account.invoice'].browse(invoice_id),
                'component': self._context.get('component')
            }
            safe_eval(line.qty_formula_id.code.strip(), eval_context,
                      mode="exec", nocopy=True)  # nocopy for returning result
            qty = eval_context.get('result', 0)
            if self.skip_zero_qty and float_is_zero(
                    qty, self.env['decimal.precision'].precision_get(
                    'Product Unit of Measure')):
                # Return empty dict to skip line create
                vals = {}
            else:
                vals['quantity'] = qty
                # Re-evaluate price with this new quantity
                vals['price_unit'] = line.with_context(
                    contract_line_qty=qty,
                ).price_unit
        return vals


class AccountAnalyticContractLine(models.Model):
    _inherit = 'account.analytic.contract.line'

    qty_type = fields.Selection(selection_add=[('component', 'Component')])

    @api.constrains('qty_type')
    def _check_code(self):
        if self.qty_type == 'component' and \
                not self.analytic_account_id.by_component:
            raise exceptions.ValidationError(_('No valid type.'))



class ContractLineFormula(models.Model):
    _inherit = 'contract.line.qty.formula'


    @api.constrains('code')
    def _check_code(self):
        eval_context = {
            'env': self.env,
            'context': self.env.context,
            'user': self.env.user,
            'line': self.env['account.analytic.invoice.line'],
            'contract': self.env['account.analytic.account'],
            'invoice': self.env['account.invoice'],
            'component': self.env['account.analytic.account.component']
        }
        try:
            safe_eval(
                self.code.strip(), eval_context, mode="exec", nocopy=True)
        except Exception as e:
            raise exceptions.ValidationError(
                _('Error evaluating code.\nDetails: %s') % e)
        if 'result' not in eval_context:
            raise exceptions.ValidationError(_('No valid result returned.'))
