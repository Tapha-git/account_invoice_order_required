# -*- coding: utf-8 -*-
{
    "name": "Invoice Order Required",
    "summary": "Block customer and vendor invoices that are not generated from sale or purchase orders",
    "version": "18.0.1.0.5",
    "category": "Accounting/Accounting",
    "author": "MMLY",
    "license": "OPL-1",
    "depends": [
        "account",
        "sale_management",
        "purchase",
    ],
    "data": [
        "security/security.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
    "installable": True,
    "application": False,
}
