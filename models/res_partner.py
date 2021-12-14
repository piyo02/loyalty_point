from odoo import fields, models, api
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    member_status = fields.Boolean(string='Member Status', default=False)
    card_number_lyt = fields.Char(string='Card Number')
    member_loyalty_level_id = fields.Many2one(comodel_name='loyalty.level.configuration', string='Member Level')
    
    earned_point_count = fields.Float(compute='_compute_earned_point_count', string='# of Earned Point Record')
    redeem_point_count = fields.Float(compute='_compute_redeem_point_count', string='# of Redeem Point Record')
    
    total_points = fields.Float(string='Total Earn Points', compute='_calculate_total_points')
    total_redeem_points = fields.Float(string='Total Redeem', compute='_calculate_partner_point')
    total_exp_earned_points = fields.Float(string='Total Expired', compute='_calculate_partner_point')
    total_remaining_points   = fields.Float("Remaining Points", compute='_calculate_partner_point', readonly=1)
    
    @api.multi
    def _calculate_total_points(self):
        EarnedPointRecord = self.env['earned.point.record'];
        for partner in self:
            records = EarnedPointRecord.search([
                ('partner_id.id', '=', partner.id),
            ])
            points_earned = 0.00
            for record in records:
                points_earned += record.points
            
            partner.total_points = points_earned

    def _compute_earned_point_count(self):
        all_partners = self.search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        EarnedPointRecord = self.env['earned.point.record'].read_group(
            domain=[('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id']
        )
        for group in EarnedPointRecord:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.earned_point_count += group['partner_id_count']
                partner = partner.parent_id

    def _compute_redeem_point_count(self):
        all_partners = self.search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        RedeemPointRecord = self.env['redeem.point.record'].read_group(
            domain=[('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id']
        )
        for group in RedeemPointRecord:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.redeem_point_count += group['partner_id_count']
                partner = partner.parent_id

    @api.multi
    def _calculate_partner_point(self):
        EarnedPointRecord = self.env['earned.point.record'];
        RedeemPointRecord = self.env['redeem.point.record']
        
        for partner in self:
            total_points = 0.00
            redeem_point = 0.00
            exp_point = 0.00
            remaining_point = 0.00

            earned_points = EarnedPointRecord.search([
                ('partner_id', '=', partner.id),
            ])
            for earned_point in earned_points:
                if earned_point.state == 'open':
                    remaining_point += earned_point.points
                else:
                    exp_point += earned_point.points
            
            redeem_points = RedeemPointRecord.search([
                ('partner_id', '=', partner.id),
            ])
            for redeem in redeem_points:
                redeem_point += redeem.points

            partner.total_points            = remaining_point + exp_point
            partner.total_redeem_points     = redeem_point
            partner.total_exp_earned_points = exp_point
            partner.total_remaining_points  = remaining_point - redeem_point