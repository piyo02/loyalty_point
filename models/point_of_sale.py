from odoo import fields, models, api
from datetime import datetime, timedelta
import logging
_logger = logging.getLogger(__name__)

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
        PosConfig = self.env['pos.config'].search([], limit=1)
        if PosConfig.enable_pos_loyalty and res.partner_id:
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
                        'state': 'open',
                        'source': 'pos'
                    }
                    self.env['earned.point.record'].create(point_vals)

                if order.get('loyalty_redeemed_point') > 0:
                    redeemed_vals = {
                        'partner_id': res.partner_id.id,
                        'points': order.get('loyalty_redeemed_point'),
                        'pos_order_id': res.id,
                        'redeem_amount': order.get('loyalty_redeemed_amount'),
                    }
                    self.env['redeem.point.record'].create(redeemed_vals)

        return res

    def _calcultae_amount_total_by_points(self, loyalty_config, point):
        return (float(point) * loyalty_config.to_amount) / loyalty_config.points

    @api.multi
    def refund(self):
        res = super(PosOrder, self).refund()

        LoyaltyPointRecord = self.env['earned.point.record']
        RedeemLoyaltyPointRecord = self.env['redeem.point.record']
        
        refund_order_id = self.browse(res.get('res_id'))

        if refund_order_id:
            redeem_val = {
                'pos_order_id': refund_order_id.id,
                'partner_id': self.partner_id.id,
                'points': refund_order_id.total_loyalty_redeem_points,
                'redeem_amount': refund_order_id.total_loyalty_redeem_amount,
                
            }
            RedeemLoyaltyPointRecord.create(redeem_val)

            point_val = {
                'pos_order_id': refund_order_id.id,
                'partner_id': self.partner_id.id,
                'points': refund_order_id.total_loyalty_earned_points * -1,
            }
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
