.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Sale Purchase Count
===================

Links MRP with sales, enabling

* Open linked purchases from sale.

Installation
============

There are no special installation instructions for this module.

Configuration
=============

None

Usage
=====

None

Known issues / Roadmap
======================

* Relies on an ilike search of origin field.  So it is possible for
  false positives if sequence is poor.
* Without a trigram index on origin (and possibly even with) performance
  may be slow as no possibility to use read group.

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
