.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Sale Price Recalculation
========================

Allows to update the pricing on confirmed sales orders and associated
draft invoices.  Included features are:

* Update from pricelist
* Update from quote
* Balance to total (tax incl or excl)
* Manual modification of any price, discount, subtotal or total


Installation
============

There are no special installation instructions for this module.

Configuration
=============

There are no specific configuration options in this module.

Usage
=====

To use this module, you need to:

#. Open a sales order that requires its pricing updated
#. Under the more menu click 'Update Pricing'
#. To update the order with your new prices click Write Changes

Known issues / Roadmap
======================

* Currently no tests.
* No domain on quotes - consider a partner and/or state based domain.
* Using multiple combinations of pricelist, quote, balance and manual adjustment can sometimes look odd.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/odoonz/sale/issues>`_. In case of trouble, please
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
