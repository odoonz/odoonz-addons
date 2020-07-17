.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
Sale Partcode Replacement
=========================

Allows a sales order to be updated by replacing part of a part code of all products in a sale order with another.

For example, if all blue products had BL in their code, and all red ones had RD, you could update the colour or the order.
In general, this module will work best with systemised partcodes and use of variants but there may be other use cases and it is
not dependent on them.

Installation
============

There are no special installation instructions for this module.

Configuration
=============

There are no specific configuration options in this module.

Usage
=====

To use this module, you need to:

#. Open a sales order.
#. From the more menu click 'Substitute Partcodes'
#. Enter the portion of partcode you wish to replace and what you wish to replace with.
#. Click Substitute.
#. The sale order will update the partcodes and pricing, based on the pricelist of the order.

Known issues / Roadmap
======================

* Currently no easy way to apply global exclusions to all affected templates.

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

* Graeme Gellatly <graeme@o4sb.com>

Maintainer
----------

This module is maintained by Open for Small Business Ltd.

Open for Small Business is a small developer and integrator of Odoo software since 2009.
