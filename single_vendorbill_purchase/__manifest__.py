# -*- coding: utf-8 -*-

{
    'name': 'Merge Purchase Orders from Single Vendor',
    'category': 'Purchase',
    'summary': 'This module will create single vendor bill of multiple purchase orders.',
    'version': '11.0.1.0.1',
    'website': 'http://www.aktivsoftware.com',
    'author': 'Aktiv Software',
    'description': 'Create single vendor bill from multiple purchase order',
    'license': "AGPL-3",
    'depends': ['purchase','account'],
    'data': [
        'wizard/single_vendor_bill_wizard_view.xml'
    ],

    'images': [
        'static/description/banner.jpg',
    ],

    'installable': True,
}
