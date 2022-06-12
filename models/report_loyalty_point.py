from odoo import api, fields, models
from datetime import date, datetime, timedelta
import time

import logging
_logger = logging.getLogger(__name__)

class ReportLolyaltyPoint(models.TransientModel):
    _name = "report.loyalty.point"

    start_date = fields.Date(string='Tanggal Awal', required=True, default=datetime.today())
    end_date = fields.Date(string='Tanggal Akhir', required=True)
    customer_ids = fields.Many2many('res.partner', string='Customer', domain="[('customer', '=', True)]")


    @api.multi
    def print_report_loyalty_point(self):
        final_dict = {}

        if len(self.customer_ids) == 0:
            self.customer_ids = self.env['res.partner'].search([('customer', '=', True)])
            
        for customer in self.customer_ids:
            last_point = self.env['earned.point.record'].search([
                ('date_obtained', '<=', self.start_date),
                ('partner_id.id', '=', customer.id),
            ], limit=1, order="id desc")
            if not last_point:
                last_point = self.env['earned.point.record'].search([
                    ('partner_id.id', '=', customer.id),
                ], limit=1, order="id asc")
            
            dict_point = {}
            datas = []
            total_point = 0

            earned_points = self.env['earned.point.record'].search([
                ('date_obtained', '>=', self.start_date),
                ('date_obtained', '<=', self.end_date),
                ('partner_id.id', '=', customer.id),
            ])
            for point in earned_points:
                total_point = total_point + point.points
                transcation = point.pos_order_id.name if point.pos_order_id else point.sale_order_id.name

                data = []
                data.append( transcation )
                data.append( point.date_obtained )
                data.append( '-' )
                data.append( point.points )
                data.append( point.expired_date )
                
                date_record = datetime.strptime(point.date_obtained, '%Y-%m-%d %H:%M:%S')
                date_timestamp = int(round( time.mktime(date_record.timetuple()) ))
                dict_point[str(date_timestamp) + 'ear'] = data

            redeem_points = self.env['redeem.point.record'].search([
                ('date_used', '>=', self.start_date),
                ('date_used', '<=', self.end_date),
                ('partner_id.id', '=', customer.id),
            ])
            for point in redeem_points:
                transcation = point.pos_order_id.name if point.pos_order_id else point.sale_order_id.name

                data = []
                data.append( transcation )
                data.append( '-' )
                data.append( point.date_used )
                data.append( point.points )
                data.append( '-' )

                date_record = datetime.strptime(point.date_used, '%Y-%m-%d %H:%M:%S')
                date_timestamp = int(round( time.mktime(date_record.timetuple()) ))
                dict_point[str(date_timestamp) + 'red'] = data

            for key in dict_point.keys():
                datas.append( dict_point[key] )
                
            customer_point = [
                last_point.total_current_point,
                datas,
                total_point,
                customer.total_exp_earned_points,
                customer.total_remaining_points,
                customer.total_points,
                customer.total_redeem_points,
            ]

            if datas:
                final_dict[customer.name] = customer_point
        
        datas = {
            'ids': self.ids,
            'model': 'report.loyalty.point',
            'form': final_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env['report'].get_action(self,'loyalty_point.loyalty_point_report_temp', data=datas)
