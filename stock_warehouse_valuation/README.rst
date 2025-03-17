=========================
Stock Warehouse Valuation
=========================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta

|badge1|

This module provides temporal stock valuation capabilities, allowing you to track historical stock values by location and warehouse. It automatically creates monthly snapshots of stock valuations and provides comprehensive analysis tools.

**Table of contents**

.. contents::
   :local:

Rationale
=========

This module addresses the lack of a temporal stock valuation feature in Odoo by warehouse or location. There are
some challenges in doing this live. Stock Valuation layers do no hold location information, stock.quants only represent
the current state. They also don't reuse the svl valuation methods of product.product which are date sensitive. Products
themselves within the Inventory At Date doesn't work with locations.

Quants also can't be grouped very easily by meaningful fields such as valuation account or warehouse.

Rather than create a mess of workarounds, or new fields on already busy tables, this solution uses a monthly cron job to 
create a snapshot of the stock valuation. This also enables some nice reporting with grpahs and pivots such as:

* Valuation by product category
* Valuation by warehouse
* Valuation by location
* Valuation by valuation account
* Valuation change over time


Configuration
=============

To configure this module, you need to:

* Go to Inventory > Configuration > Settings
* Ensure you have "Storage Locations" enabled
* Ensure you have "Multi-Warehouses" enabled if you want to track valuations across multiple warehouses

Usage
=====

To use this module, you need to:

#. Go to Inventory > Reporting > Stock Valuation History
#. View historical stock valuations by:
    * Product
    * Product Category
    * Warehouse
    * Location
#. Use the graph view to analyze valuation trends
#. Use the pivot view for detailed analysis across different dimensions

The module will automatically:

* Create monthly snapshots of stock valuations
* Store historical valuation data
* Track values by location and warehouse
* Maintain product category information

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/odoonz/odoonz-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`feedback <https://github.com/odoonz/odoonz-addons/issues/new?body=module:%20stock_warehouse_valuation%0Aversion:%2016.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Graeme Gellatly

Contributors
~~~~~~~~~~~~

* Graeme Gellatly <graeme@moahub.nz>
