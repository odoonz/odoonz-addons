.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================
Account Invoice Cutoff Policy
=============================

Allows to specify a customer specific invoice policy.  The policy can be based
either on the transaction date or the end of month and can be any number of
days, or weekdays in the future.

Invoices will be automatically redated on validation if they fall outside the policy, either to the
1st day of the month (end of month) or todays date.

Installation
============

There are no special installation instructions for this module.

Configuration
=============

There are no special configuration instructions for this module.

Usage
=====

Login as a user with Accounting Adviser access rights
Go to Sales -> Customers and select a customer to specify a cutoff policy for.
Under Accounting Settings check enforce cutoff and complete policy.

Note the policy is inclusive, so if you specified 3 days after end of month, then transactions
on the 3rd for the prior month would be allowed, the 4th would not.

If using account_central_billing the policy is taken from the centrally billed partner.

Known issues / Roadmap
======================

* Currently no tests.
* Using negatives has not been tested and no validation around that.
* Not multicompany aware.

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

* Graeme Gellatly <g@o4sb.com>

Maintainer
----------

This module is maintained by Open for Small Business Ltd.

Open for Small Business is a small developer and integrator of Odoo software since 2009.
