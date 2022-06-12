{
    'name': 'Loyalty Member',
    'category': 'Hidden',
    'summary': 'Implement Loyalty Member in POS Order and Sale Order',
    'description': """
Config:
""",
    'author': 'TechnoIndo',
    'website': 'http://www.technoindo.com',
    'version': '1.0.1',
    'depends': [
        'base',
        'point_of_sale',
        'sale',
        'config_cashback_loyalty',
    ],
    "data": [
        'report/loyalty_point_report_temp.xml',
        'report/loyalty_point_report.xml',
        'views/account_payment_view.xml',
        'views/loyalty_config_view.xml',
        'views/loyalty_point.xml',
        'views/point_of_sale.xml',
        'views/sale_order.xml',
        'views/scheduler.xml',
        'views/sequence.xml',
        'views/view_partner.xml',
        'wizards/report_loyalty_point.xml',
        'wizards/sale_config_view.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/icon.png'],
    'qweb': [
        'static/src/xml/pos.xml'
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}