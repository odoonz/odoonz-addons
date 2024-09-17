# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Price Recalculation",
    "summary": "Allows to update the pricing on confirmed sales orders "
    "prior to invoice",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": " Open For Small Business Ltd",
    "website": "https://github.com/OCA/project",
    "depends": ["price_recalculation", "sale"],
    "data": ["wizards/sale_price_recalculation.xml", "security/ir.model.access.csv"],
    "installable": False,
}
