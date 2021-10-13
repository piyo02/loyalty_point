from odoo import fields, models, api
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

class PosOrderRedeem(models.Model):
    _name = 'pos.order.redeem'

    pos_order_id = fields.Many2one('pos.order', string='Reference', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    points = fields.Float(string='Points')
    redeem_amount = fields.Float(string='Redeem Amount')
    
class PosOrderPoint(models.Model):
    _name = 'pos.order.point'

    amount_total = fields.Float('Total Amount', readonly=1)
    pos_order_id = fields.Many2one('pos.order', string='Reference', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    points = fields.Float(string='Points')
    expired_date = fields.Datetime(string='Expired Date', compute='_calculate_expired_date')
    status = fields.Integer('Status', compute='_status_point')
    source = fields.Selection([('so', 'Sale Order'), ('pos', 'Point of Sale')], string='Source Point', default='pos')

    @api.multi
    def _status_point(self):
        for rec in self:
            expired_date = datetime.now() + timedelta(days=rec.partner_id.member_loyalty_level_id.expired_day)
            if rec.expired_date < expired_date:
                rec.status = 0
            else:
                rec.status = 1

    @api.multi
    def _calculate_expired_date(self):
        for rec in self:
            loyalty_level_id = self.env['loyalty.level.configuration'].search([
                ('id', '=', rec.partner_id.member_loyalty_level_id.id)
            ], limit=1)
            _logger.warning( rec.pos_order_id.date_order )
            date = datetime.strptime(rec.pos_order_id.date_order, '%Y-%m-%d %H:%M:%S')
            rec.expired_date = date + timedelta(days=loyalty_level_id.expired_day)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    total_loyalty_earned_points = fields.Float("Earned Loyalty Points")
    total_loyalty_earned_amount = fields.Float("Earned Loyalty Amount")
    total_loyalty_redeem_points = fields.Float("Redeemed Loyalty Points")
    total_loyalty_redeem_amount = fields.Float("Redeemed Loyalty Amount")

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        res.update({
            'total_loyalty_earned_amount': ui_order.get('loyalty_earned_amount') or 0.00,
            'total_loyalty_earned_points': ui_order.get('loyalty_earned_point') or 0.00,
            'total_loyalty_redeem_amount': ui_order.get('loyalty_redeemed_amount') or 0.00,
            'total_loyalty_redeem_points': ui_order.get('loyalty_redeemed_point') or 0.00,
        })
        return res

    @api.model
    def _process_order(self, order):
        res = super(PosOrder, self)._process_order(order)
        LoyaltyConfig = self.env['loyalty.config'].search([], limit=1)
        _logger.warning(order)
        if LoyaltyConfig.enable_loyalty and res.partner_id:
            loyalty_level_id = self.env['loyalty.level.configuration'].search([
                ('id', '=', res.partner_id.member_loyalty_level_id.id)
            ], limit=1)
            if loyalty_level_id:
                if order.get('loyalty_earned_point') > 0 and res.partner_id.member_status:
                    point_vals = {
                        'amount_total': (float(order.get('loyalty_earned_point')) * loyalty_level_id.to_amount) / loyalty_level_id.points,
                        'expired_date': datetime.now() + timedelta(days=loyalty_level_id.expired_day),
                        'partner_id': res.partner_id.id,
                        'points': order.get('loyalty_earned_point'),
                        'pos_order_id': res.id,
                        'status': 1,
                        'source': 'pos'
                    }
                    self.env['pos.order.point'].create(point_vals)
                    self.env['loyalty.point.record'].create(point_vals)

                if order.get('loyalty_redeemed_point') > 0:
                    redeemed_vals = {
                        'partner_id': res.partner_id.id,
                        'points': order.get('loyalty_redeemed_point'),
                        'pos_order_id': res.id,
                        'redeem_amount': order.get('loyalty_redeemed_amount'),
                    }
                    self.env['pos.order.redeem'].create(redeemed_vals)
                    self.env['redeem.loyalty.point.record'].create(redeemed_vals)

        return res

    def _calcultae_amount_total_by_points(self, loyalty_config, point):
        return (float(point) * loyalty_config.to_amount) / loyalty_config.points

    @api.multi
    def refund(self):
        res = super(PosOrder, self).refund()
        LoyaltyPoints = self.env['loyalty.point']

        PosOrderPoint = self.env['pos.order.point']
        LoyaltyPointRecord = self.env['loyalty.point.record']
        PosOrderRedeem = self.env['pos.order.redeem']
        RedeemLoyaltyPointRecord = self.env['redeem.loyalty.point.record']
        
        refund_order_id = self.browse(res.get('res_id'))

        if refund_order_id:
            redeem_val = {
                'pos_order_id': refund_order_id.id,
                'partner_id': self.partner_id.id,
                'points': refund_order_id.total_loyalty_redeem_points,
                'redeem_amount': refund_order_id.total_loyalty_redeem_amount,
                
            }
            PosOrderRedeem.create(redeem_val)
            RedeemLoyaltyPointRecord.create(redeem_val)

            point_val = {
                'pos_order_id': refund_order_id.id,
                'partner_id': self.partner_id.id,
                'points': refund_order_id.total_loyalty_earned_points * -1,
                
            }
            PosOrderPoint.create(point_val)
            LoyaltyPointRecord.create(point_val)

            refund_order_id.write({
                'total_loyalty_earned_points': refund_order_id.total_loyalty_earned_points * -1,
                'total_loyalty_earned_amount': refund_order_id.total_loyalty_earned_amount * -1,
                'total_loyalty_redeem_points': 0.00,
                'total_loyalty_redeem_amount': 0.00,
            })
        return res

class PosConfig(models.Model):
    _inherit = "pos.config"

    enable_pos_loyalty = fields.Boolean("Enable Loyalty")
    loyalty_journal_id = fields.Many2one("account.journal","Loyalty Journal")

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.model
    def name_search(self, name,args=None, operator='ilike', limit=100):
        if self._context.get('loyalty_jr'):
            if self._context.get('journal_ids') and \
               self._context.get('journal_ids')[0] and \
               self._context.get('journal_ids')[0][2]:
               args += [['id', 'in', self._context.get('journal_ids')[0][2]]]
            else:
                return False;
        return super(AccountJournal, self).name_search(name, args=args, operator=operator, limit=limit)
