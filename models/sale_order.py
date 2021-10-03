from odoo import fields, models, api
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class SaleOrderRedeem(models.Model):
    _name = 'sale.order.redeem'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    points = fields.Float(string='Points')
    redeem_amount = fields.Float(string='Redeem Amount')
    sale_order_id = fields.Many2one('sale.order', string='Reference', required=True)

class SaleOrderPoint(models.Model):
    _name = 'sale.order.point'

    amount_total = fields.Float('Total Amount', readonly=1)
    expired_date = fields.Datetime(string='Expired Date', default=datetime.now())
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    points = fields.Float(string='Points')
    sale_order_id = fields.Many2one('sale.order', string='Reference', required=True)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    available_redeem_point = fields.Boolean('Available Redeem Point', default=False)
    loyalty_journal_id = fields.Many2one("account.journal", "Loyalty Journal")
    redeem_status = fields.Boolean('Use Redeem Point', default=False)

    @api.depends('redeem_status')
    @api.onchange('redeem_status')
    def _set_loyalty_journal_id(self):
        self.ensure_one()
        for rec in self:
            enable_pos_loyalty = rec.env.user.company_id.enable_pos_loyalty
            loyalty_journal_id = rec.env.user.company_id.loyalty_journal_id
            if enable_pos_loyalty and loyalty_journal_id and rec.redeem_status:
                rec.loyalty_journal_id = loyalty_journal_id
    
    @api.depends('partner_id')
    @api.onchange('partner_id')
    def _check_member_status(self):
        self.ensure_one()
        for rec in self:
            enable_pos_loyalty = rec.env.user.company_id.enable_pos_loyalty
            if enable_pos_loyalty and rec.partner_id.member_status:
                rec.available_redeem_point = True
                return
        
        rec.available_redeem_point = False
        return 
        
class SaleAdvancedPaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.multi
    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        enable_pos_loyalty = self.env.user.company_id.enable_pos_loyalty
        loyalty_journal_id = self.env.user.company_id.loyalty_journal_id

        # if sale_orders.redeem_status and enable_pos_loyalty and loyalty_journal_id:
            # if self.advance_payment_method == 'all':
            #     _logger.warning( 'create_invoices all' )
            #     return

        res = super(SaleAdvancedPaymentInv, self).create_invoices()
        

