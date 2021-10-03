from odoo import fields, models, api
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class LoyaltyConfig(models.Model):
    _name = 'loyalty.config'

    enable_loyalty = fields.Boolean('Enable Loyalty')
    loyalty_journal_id = fields.Many2one('account.journal', 'Loyalty Journal', required=True)
    account_id = fields.Many2one('account.account', string='Cash Account', domain=[('deprecated', '=', False)], required=True)

class LoyaltyLevelConfiguration(models.Model):
    _name = 'loyalty.level.configuration'

    name = fields.Char(string='Name', required=True)
    expired_day = fields.Integer(string='Expired (Day)')
    minimum_purchase = fields.Float(string='Minimum Purchase', required=True)
    point_calculation = fields.Float(string='Point Calculation (%)', required=True)
    points = fields.Integer(String='Points', required=True)
    to_amount = fields.Float(string='To Amount (Rp)', required=True)

class LoyaltyPointRecord(models.Model):
    _name = 'loyalty.point.record'

    amount_total = fields.Float('Total Amount', readonly=1)
    expired_date = fields.Datetime(string='Expired Date', default=datetime.now(), readonly=1)
    partner_id = fields.Many2one('res.partner', 'Customer', required=True, readonly=1)
    points = fields.Float(string='Points', readonly=1)
    pos_order_id = fields.Many2one('pos.order', string='POS Order', readonly=1)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=1)

class RedeemLoyaltyPointRecord(models.Model):
    _name = 'redeem.loyalty.point.record'

    partner_id = fields.Many2one('res.partner', 'Customer', required=True, readonly=1)
    points = fields.Float(string='Points', required=True, readonly=1)
    pos_order_id = fields.Many2one('pos.order', string='POS Order', readonly=1)
    redeem_amount = fields.Float(string='Redeem Amount', required=True, readonly=1)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=1)