.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Account Journal Lock Policy
===========================

Allows to specify a lock date policy at the journal level.  The policy can be based
either on the transaction date or the end of month and can be any number of months,
days, or weekdays in the future.

Installation
============

There are no special installation instructions for this module.

Configuration
=============

There are no special configuration instructions for this module.

Usage
=====

Go to Accounting -> Settings -> Journals
Under Advanced Settings check enforce lock and complete policy.

Note the policy is exclusive, so if you specified 3 days after end of month, then transactions
on the 3rd for the prior month would not be allowed.

Known issues / Roadmap
======================

* Currently no tests.
* Using negatives has not been tested and no validation around that.

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
