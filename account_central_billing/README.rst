.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
Account Central Billing
=======================

Sometimes it is necessary to invoice a partner who is a different entity to the one ordering, such as when dealing
with large buying groups.  This module automatically changes the invoice from the purchasing entity to the invoice
entity.

Supports recursive billing.  So if all invoices to Branch A are billed to Partner A, from Company B, then
Company C invoices for Branch and Partner A will go to Company B, whereas Company B invoices to Branch A will go
to Partner A.

Installation
============

There are no special installation instructions for this module.

Configuration
=============

#. For each centrally billed partner, select the appropriate supplier or customer billing option.
#. Specify the partner to bill / receive bills from

Usage
=====

Once a partner is configured, there are no usage instructions for regular users, invoices are automatically billed.
You can search for invoices either using the billing or purchasing entity.

Known issues / Roadmap
======================

* Currently no tests.

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

* Graeme Gellatly <graeme@o4sb.com>

Maintainer
----------

This module is maintained by Open for Small Business Ltd.

Open for Small Business is a small developer and integrator of Odoo software since 2009.
