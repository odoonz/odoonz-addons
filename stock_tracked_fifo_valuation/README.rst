============================
Stock Tracked Fifo Valuation
============================

PLEASE NOTE: As of v16 I have found an alternate way of achieving this for my client requirements.
I will not be maintaining this module further. If you wish to take over maintenance please contact me.

This module extends the functionality of `stock_account` to pick the valuation
of in_moves for FIFO valuation only from those available lots on the order.

It will work perfectly in a perfect scenario, whereby the oldest lot is
available in the exact qty shipped, or just 1 lot. Otherwise it falls
back to the default behaviour.




**Table of contents**

.. contents::
   :local:

Usage
=====

To use this module, you need to:

#. Install it, be using FIFO inventory tracking and serial or lot tracking for
   at least 1 product. Nothing else.

Known issues / Roadmap
======================

* Better support the quantities case, whereby different quantities of
  different lots are sent.

Changelog
=========

12.0.1.0.0 (2019-01-04)
~~~~~~~~~~~~~~~~~~~~~~~

* [NEW] Initial module release

Authors
~~~~~~~

* Graeme Gellatly

Contributors
~~~~~~~~~~~~

* Graeme Gellatly <graeme@moahub.nz> (https://moahub.nz)
