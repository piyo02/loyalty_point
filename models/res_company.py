from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    enable_pos_loyalty = fields.Boolean("Enable Loyalty")
    loyalty_journal_id = fields.Many2one("account.journal", "Loyalty Journal")