=====================================
Stock Filter Show Qty Mrp Glue Bugfix
=====================================

Fixes context incompatibility of mrp, stock_filter_qty and stock_show_qty

Configuration
=============

This module autoinstalls as soon as you have the incompatible modules installed. It is
a technical fix to an odoo upstream issue overwriting the context of the stock.move.line
tree view.

Changelog
=========

1.0.0 (2022-12-05)
------------------
Initial Implementation
