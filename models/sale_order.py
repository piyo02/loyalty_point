from odoo import fields, models, api
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    available_redeem_point = fields.Boolean('Available Redeem Point', default=False)
    loyalty_journal_id = fields.Many2one("account.journal", "Loyalty Journal")
    redeem_status = fields.Boolean('Use Redeem Point', default=False)

    @api.depends('partner_id')
    @api.onchange('partner_id')
    def _check_member_status(self):
        self.ensure_one()
        for rec in self:
            enable_pos_loyalty = rec.env.user.company_id.enable_pos_loyalty
            if enable_pos_loyalty and rec.partner_id.member_status and rec.partner_id.total_remaining_points:
                rec.available_redeem_point = True
                return
        
        rec.available_redeem_point = False
        return 