from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)

class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    enable_pos_loyalty = fields.Boolean("Enable Loyalty")
    loyalty_journal_id = fields.Many2one("account.journal","Loyalty Journal")

    @api.multi
    def set_enable_pos_loyalty_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'enable_pos_loyalty', self.enable_pos_loyalty
        )
    
    @api.multi
    def set_loyalty_journal_id_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'loyalty_journal_id', self.loyalty_journal_id.id
        )