.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================
Reordering Rule Quantity Multiple
=================================

Round a reordering rule's quantity to order up to an integer multiple,
without creating a packaging.

Odoo 19 replaced the old ``qty_multiple`` float with a replenishment
unit. This module adds **Quantity Multiple** back as an integer. When
that value is set and the replenishment unit is empty, the quantity to
order is rounded up to a multiple of it. The rounding uses the standard
replenishment calculation: the module builds an in-memory unit whose
size is the multiple and returns it from
``_get_replenishment_multiple_alternative``. The unit is not saved.

A replenishment unit on the rule still wins. A multiple of 0 leaves the
standard fallback in place: the vendor's unit on a Buy route, or the
bill of materials unit on a Manufacture route.

The module depends on Purchase and Manufacturing so this fallback is
applied ahead of those modules. They replace the same method and do not
call ``super`` when their route matches.

Installation
============

Install **Reordering Rule Quantity Multiple**. Purchase and
Manufacturing are installed with it.

Configuration
=============

No configuration is required.

Usage
=====

On a reordering rule, or on Inventory → Operations → Replenishment,
set **Quantity Multiple**.

* ``10`` rounds a need of 15.5 up to 20.
* ``0`` does not round. A Buy or Manufacture route can still round to
  the vendor unit or the bill of materials unit.
* A replenishment unit on the same rule is used instead of the multiple.

The **Multiple** column shows the number in grey while the replenishment
unit is empty, because that column's placeholder is the name of the
in-memory unit.

Known issues / Roadmap
======================

* The multiple is a whole number. Fractional multiples, such as 2.5,
  are not supported.
* Rounding is always up, including when a maximum quantity is set.
  Odoo 18 rounded down in that case so the order stayed within the
  maximum.

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
