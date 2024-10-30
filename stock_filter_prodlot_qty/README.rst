.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================
Stock Filter Lot Quantity
=============================

Technical module that filters lots available in a location name if context
location key is set.

Installation
============

There are no special installation instructions for this module.

Configuration
=============

Many views already pass a location_id in context and this module will
work without modification. Where they do not, you will need to add to
the requisite view (technical job)

Usage
=====

None

Known issues / Roadmap
======================

* extend to accept warehouse as context key
* currently uses quants.quantity - available_qty may be better or an option

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
