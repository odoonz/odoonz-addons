.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Financial Invoices & Credits
============================

By default Odoo will create Stock Entries for all COGS eligible products on invoices and credit notes. Often
this is the opposite of what is required, and stock entries must not be created. A simple example is overcharging
a customer and raising a credit note for the difference. In this case we only wish to reduce our revenue and leave
our stock accounts unaffected. Likewise if overcharged by a supplier, typically amounts are immaterial and just
posted to COGS rather than the stock input account.

Installation
============

There are no special installation instructions for this module.

Usage
=====

This module tries to use sensible defaults. If creating an invoice or credit manually, i.e. clicking the new
button, this will default to being a financial invoice. If creation comes from a sale or purchase, it will default
to stock. In a supplier invoice, adding a purchase order automatically changes to stock.

With credit notes, when the reversal wizard shows an additional dropdown is shown to choose between stock and financial.
This will only affect reversals. If selecting reverse and modify, these will always be stock invoices. In part this is
due to a limitation in Odoo reversal logic, and in part there is a particular case where even if stock is unaffected we
still want to have stock entries, namely where the wrong supplier or customer was used. And in all other cases, the
stock figures either balance out, or if changing quantities, they should be changed.

Known issues / Roadmap
======================

* Currently only tests for sales.

Changelog
=========

18.0.1.0.0
----------
#. Ribbon replaced by banner to avoid the case of multiple ribbons layering.
#. Code refactored for readability and context
#. Tests for sales added
#. Readme added

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/odoonz/odoonz-addons/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Graeme Gellatly <graeme@moahub.nz>

Maintainer
----------

This module is maintained by MoaHub Ltd.

MoaHub is a small developer and integrator of Odoo software since 2009.
