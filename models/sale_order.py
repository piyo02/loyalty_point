from odoo import fields, models, api, _
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    available_redeem_point = fields.Boolean('Available Redeem Point', default=False)
    available_loyalty_point = fields.Boolean('Available Loyalty Point', default=False)
    loyalty_journal_id = fields.Many2one("account.journal", "Loyalty Journal")
    redeem_status = fields.Boolean('Use Redeem Point', default=False)
    is_get_loyalty_point = fields.Boolean('Get Loyalty Point?', default=False)

    @api.depends('partner_id')
    @api.onchange('partner_id')
    def _check_member_status(self):
        self.ensure_one()
        for rec in self:
            enable_pos_loyalty = self.env['ir.values'].get_default('sale.config.settings', 'enable_pos_loyalty')
            _logger.warning( enable_pos_loyalty )
            _logger.warning( rec.partner_id.member_status )
            if enable_pos_loyalty and rec.partner_id.member_status :
                rec.available_loyalty_point = True
                if rec.partner_id.total_remaining_points:
                    rec.available_redeem_point = True
                return
        
        rec.available_redeem_point = False
        rec.available_loyalty_point = False
        return