from odoo import fields, models, api
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)


class LoyaltyConfig(models.Model):
    _name = 'loyalty.config'

    # ref = fields.Char(string='Referensi', readonly=True, default='/')
    enable_loyalty = fields.Boolean('Enable Loyalty')
    loyalty_journal_id = fields.Many2one('account.journal', 'Loyalty Journal', required=True)
    account_id = fields.Many2one('account.account', string='Cash Account', domain=[('deprecated', '=', False)], required=True)

class LoyaltyLevelConfiguration(models.Model):
    _name = 'loyalty.level.configuration'

    # ref = fields.Char(string='Referensi', readonly=True, default='/')
    name = fields.Char(string='Name', required=True)
    expired_day = fields.Integer(string='Expired (Day)')
    minimum_purchase = fields.Float(string='Minimum Purchase', required=True)
    point_calculation = fields.Float(string='Point Calculation (%)', required=True)
    points = fields.Integer(String='Points', required=True)
    to_amount = fields.Float(string='To Amount (Rp)', required=True)

    # @api.model
    # def create(self, vals):
    #     vals['ref'] = self.env['ir.sequence'].next_by_code('loyalty.level.configuration')
    #     return super(LoyaltyLevelConfiguration, self).create(vals)

    # def copy(self, default=None):
    #     default = dict(default or {})
    #     default.update(name=("%s (copy)") % (self.name or ''))
    #     return super(LoyaltyLevelConfiguration, self).copy(default)




class LoyaltyPointRecord(models.Model):
    _name = 'loyalty.point.record'

    # ref = fields.Char(string='Referensi', readonly=True, default='/')
    amount_total = fields.Float('Total Amount', readonly=1)
    expired_date = fields.Datetime(string='Expired Date', default=datetime.now(), readonly=1)
    partner_id = fields.Many2one('res.partner', 'Customer', required=True, readonly=1)
    points = fields.Float(string='Points', readonly=1)
    pos_order_id = fields.Many2one('pos.order', string='POS Order', readonly=1)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=1)
    status = fields.Integer('Status', compute='_status_point')
    source = fields.Selection([('so', 'Sale Order'), ('pos', 'Point of Sale')], string='Source Point', default='so')

    # @api.model
    # def create(self, vals):
    #     vals['ref'] = self.env['ir.sequence'].next_by_code('loyalty.level.configuration')
    #     return super(LoyaltyLevelConfiguration, self).create(vals)

    # def copy(self, default=None):
    #     default = dict(default or {})
    #     default.update(name=("%s (copy)") % (self.name or ''))
    #     return super(LoyaltyLevelConfiguration, self).copy(default)


    @api.multi
    def _status_point(self):
        _logger.warning('_status_point')
        for rec in self:
            expired_date = datetime.now() + timedelta(days=rec.partner_id.member_loyalty_level_id.expired_day)
            loyalty_date =  datetime.strptime(rec.expired_date, '%Y-%m-%d %H:%M:%S')
           
            if loyalty_date < expired_date:
                rec.status = 0
            else:
                rec.status = 1

class RedeemLoyaltyPointRecord(models.Model):
    _name = 'redeem.loyalty.point.record'

    # ref = fields.Char(string='Referensi', readonly=True, default='/')
    partner_id = fields.Many2one('res.partner', 'Customer', required=True, readonly=1)
    points = fields.Float(string='Points', required=True, readonly=1)
    pos_order_id = fields.Many2one('pos.order', string='POS Order', readonly=1)
    redeem_amount = fields.Float(string='Redeem Amount', required=True, readonly=1)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=1)