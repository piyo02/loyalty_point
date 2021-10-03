from odoo import fields, models, api

class SaleConfiguration(models.TransientModel):
    _inherit = 'sale.config.settings'

    enable_pos_loyalty = fields.Boolean("Enable Loyalty")
    loyalty_journal_id = fields.Many2one("account.journal","Loyalty Journal")

    @api.multi
    def set_enable_pos_loyalty(self):
        self.ensure_one()
        user = self.env['res.users'].browse(self.env.uid)
        user.company_id.enable_pos_loyalty = self.enable_pos_loyalty

    @api.multi
    def get_enable_pos_loyalty(self):
        if 'enable_pos_loyalty' not in fields:
            return {}
        user = self.env['res.users'].browse(self.env.uid)
        enable_pos_loyalty = user.company_id.enable_pos_loyalty or False
        res = {'enable_pos_loyalty' : enable_pos_loyalty}
        return res

    @api.multi
    def set_loyalty_journal_id(self):
        self.ensure_one()
        user = self.env['res.users'].browse(self.env.uid)
        user.company_id.loyalty_journal_id = self.loyalty_journal_id

    @api.multi
    def get_loyalty_journal_id(self):
        if 'loyalty_journal_id' not in fields:
            return {}
        user = self.env['res.users'].browse(self.env.uid)
        loyalty_journal_id = user.company_id.loyalty_journal_id or False
        res = {'loyalty_journal_id' : loyalty_journal_id}
        return res