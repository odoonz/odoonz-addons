.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============
Partner Lock
============

This module allows you to select certain partners that cannot be edited by normal users.
The use case the led to the development of this module was multicompany environment with
shared vendors where users would deliberately and inadvertently change key details of
suppliers as well as company records.

Installation
============

There are no special installation instructions for this module.

Usage
=====

Locked partners will appear with a banner indicating they are locked. A member of the Unlock
Partners security group can unlock. lock or edit locked records. Normal users can only update
certain fields, usually ones used by automatic processes, but also allows adding child contacts.

This list of fields can be extended via development and adding (or removing) fields in the function
`_unlocked_fields`

Changelog
=========

18.0.1.0.0
----------
#. Allow unlock security group to also edit locked partners, reducing errors from the Unlock, Edit, Unlock process.
#. Code refactored for readability and context
#. Banner now to indicate to user that partner is locked, reducing frustration.
#. Tests added
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
