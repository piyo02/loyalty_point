{
    'name': 'Loyalty Point',
    'category': 'Hidden',
    'summary': 'This module allows customers earn loyalty points.',
    'description': """
This module allows customers earn loyalty points.
""",
    'author': 'TechnoIndo',
    'website': 'http://www.technoindo.com',
    'version': '1.0.1',
    'depends': ['base', 'point_of_sale', 'sale'],
    "data": [
        'views/account_payment_view.xml',
        'views/loyalty_config_view.xml',
        'views/loyalty_point.xml',
        # 'views/point_of_sale.xml',
        # 'views/sale_order.xml',
        'views/view_partner.xml',
        'wizards/sale_config_view.xml',
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