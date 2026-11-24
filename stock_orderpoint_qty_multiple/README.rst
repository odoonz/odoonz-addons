.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================
Reordering Rule Quantity Multiple
=================================

Round a reordering rule's quantity to order to an integer multiple,
without creating a packaging, and optionally keep that order within the
rule's maximum quantity.

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

The module also offers **maximum quantity protection**. Rounding up to
a whole multiple can order past **Max Quantity**. Take a rule with a
maximum of 30, 8 units on hand and a multiple of 20, say a pallet:

* The rule needs 22 to reach the maximum.
* 22 rounds up to two pallets, so 40 is ordered.
* Stock ends at 48, which is 18 over the maximum.

Odoo 18 rounded down whenever a maximum was set, precisely to avoid
this. Enabling the ``stock.orderpoint_not_to_exceed_max`` system
parameter restores that behaviour: one pallet is ordered, stock ends at
28 and the maximum is never exceeded. It is off by default and applies
to every reordering rule at once.

Installation
============

Install **Reordering Rule Quantity Multiple**. Purchase and
Manufacturing are installed with it.

Configuration
=============

No configuration is required to round up to a multiple.

For maximum quantity protection, set ``stock.orderpoint_not_to_exceed_max``
to ``True`` under Settings → Technical → System Parameters. Leaving the
parameter unset keeps Odoo's standard rounding up.

Usage
=====

On a reordering rule, or on Inventory → Operations → Replenishment,
set **Quantity Multiple**.

* ``10`` rounds a need of 15.5 up to 20.
* ``0`` does not round. A Buy or Manufacture route can still round to
  the vendor unit or the bill of materials unit.
* A replenishment unit on the same rule is used instead of the multiple.

With ``stock.orderpoint_not_to_exceed_max`` enabled, a need of 15.5
with a multiple of 10 orders 10 rather than 20. A need smaller than one
whole multiple orders nothing at all, so a rule whose maximum it cannot
reach in whole multiples stops ordering.

The **Multiple** column shows the number in grey while the replenishment
unit is empty, because that column's placeholder is the name of the
in-memory unit.

Known issues / Roadmap
======================

* The multiple is a whole number. Fractional multiples, such as 2.5,
  are not supported.
* Rounding down applies to every reordering rule at once. It cannot be
  enabled for a single rule.

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
