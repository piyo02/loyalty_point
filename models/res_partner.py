from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    card_number = fields.Char(string='Card Number')
    loyalty_point_count = fields.Float(compute='_compute_loyalty_point_count', string='# of Loyalty Point')
    member_status = fields.Boolean(string='Member Status', default=False)
    member_loyalty_level_id = fields.Many2one(comodel_name='loyalty.level.configuration', string='Member Level')
    total_points = fields.Float(string='Total Points', compute='_calculate_total_points')

    remaining_loyalty_amount = fields.Float("Points to Amount", readonly=1, compute='_calculate_remaining_loyalty')
    remaining_loyalty_points = fields.Float("Remaining Loyalty Points", readonly=1, compute='_calculate_remaining_loyalty')
    total_remaining_points   = fields.Float("Total Loyalty Points", related='remaining_loyalty_points', readonly=1)

    @api.multi
    def _calculate_total_points(self):
        LoyaltyPointRecord = self.env['loyalty.point.record'];
        for partner in self:
            records = LoyaltyPointRecord.search([
                ('partner_id.id', '=', partner.id),
            ])
            points_earned = 0.00
            for record in records:
                points_earned += record.points
            
            partner.total_points = points_earned

    def _compute_loyalty_point_count(self):
        all_partners = self.search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        LoyaltyPointRecord = self.env['loyalty.point.record'].read_group(
            domain=[('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id']
        )
        for group in LoyaltyPointRecord:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.loyalty_point_count += group['partner_id_count']
                partner = partner.parent_id

    @api.multi
    def _calculate_remaining_loyalty(self):
        LoyaltyPointRecord = self.env['loyalty.point.record'];
        RedeemLoyaltyPointRecord = self.env['redeem.loyalty.point.record']
        for partner in self:
            points_earned = 0.00
            amount_earned = 0.00
            points_redeemed = 0.00
            amount_redeemed = 0.00
            for earned_loyalty in LoyaltyPointRecord.search([('partner_id', '=', partner.id)]):
                points_earned += earned_loyalty.points
                amount_earned += earned_loyalty.amount_total
            for redeemed_loyalty in RedeemLoyaltyPointRecord.search([('partner_id', '=', partner.id)]):
                points_redeemed += redeemed_loyalty.points
                amount_redeemed += redeemed_loyalty.redeem_amount
            
            partner.remaining_loyalty_points = points_earned - points_redeemed
            partner.remaining_loyalty_amount = amount_earned - amount_redeemed
            partner.total_remaining_points = points_earned - points_redeemed