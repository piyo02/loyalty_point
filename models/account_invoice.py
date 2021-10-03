from odoo import fields, models, api
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'



    @api.multi
    def action_invoice_open(self):
        _logger.warning('action_invoice_open')

    

class AccountPayment(models.Model):
    _inherit = "account.payment"

    redeem_point = fields.Float('Redeem Point')
    redeem_amount = fields.Float('Amount Total from Redeem Point', readonly=True, compute='_calculate_redeem_amount')
    total_points = fields.Float('Total Points')

    # @api.onchange('amount', 'redeem_amount')
    def _check_available_payment(self):
        for rec in self:
            if rec.amount + rec.redeem_amount > rec.invoice_ids.residual:
                return

            if rec.amount + rec.redeem_amount < rec.invoice_ids.residual:
                return

    @api.multi
    def _calculate_redeem_amount(self):
        for rec in self:
            if rec.redeem_point and rec.invoice_ids.partner_id.member_status:
                if rec.redeem_point > total_points:
                    return "warning"
                rec.redeem_amount = rec.redeem_point * rec.invoice_ids.partner_id.member_loyalty_level_id.to_amount

    @api.multi
    def _calculate_earned_point(self):
        member_loyalty
    
    @api.multi
    def post(self):
        SaleOrderPoint = self.env['sale.order.point']
        SaleOrderRedeem = self.env['sale.order.redeem']
        member_loyalty = self.invoice_ids.partner_id.member_loyalty_id

        res = super(AccountPayment, self).post()

        name = self.invoice_ids.origin
        sale_order = self.env['sale.order'].search([
            ('name', '=', name)
        ])
        if sale_order.redeem_status:
            self._check_available_payment()
            if self.redeem_point > 0:
                SaleOrderRedeem.create({
                    'partner_id': self.invoice_ids.partner_id.id,
                    'points': self.redeem_point,
                    'redeem_amount': self.redeem_amount,
                    'sale_order_id', sale_order.id,
                })
            # create journal loyalty

            # get earned point
            earned_point = (self.invoice_ids.amount_total - self.redeem_amount) * member_loyalty.point_calculation
            SaleOrderPoint.create({
                'amount_total': ((earned_point) * member_loyalty.to_amount)/* member_loyalty.points,
                'expired_date': datetime.now() + timedelta(days=member_loyalty.expired_day),
                'partner_id': self.invoice_ids.partner_id.id,
                'points': earned_point,
                'sale_order_id': sale_order.id,
            })

        return res

    