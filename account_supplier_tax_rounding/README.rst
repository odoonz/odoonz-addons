.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================
Account Supplier Tax Rounding
=============================

Ordinarily in an ex tax environment rounding is performed
on the ex tax total.  However some suppliers may round early
at the line level.  This module allows you to configure this
easing the entry of vendor invoices and 1c rounding errors.

Installation
============

There are no special installation instructions for this module.

Configuration
=============

#. For each supplier, select the appropriate Purchase Tax rounding option.
#. Suppliers default to the company method, so only those that differ need consideration.

Usage
=====

Once a partner is configured, there are no usage instructions for regular users,
invoices are automatically calculated using the tax configuration.

Known issues / Roadmap
======================

* Only works if company policy is set to round globally

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/odoonz/account/issues>`_. In case of trouble, please
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
