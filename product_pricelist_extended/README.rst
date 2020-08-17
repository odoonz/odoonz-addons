.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Pricelist Extensions
====================

This module allows pricelist to be configured using more than just a single product or variant.

In addition it disassociates the concept of a category for pricing purposes vs a product category for stock and
accounting purposes.  When adding pricelist items a user can select multiple products or variants,
or can create seperate pricing categories for products to use in a pricelist.

Within a pricelist rule at the category or product level, there are 2 options to restrict its applicability. This
relies on partcodes, so you can specify that certain characters must, or must not be present in the partcode.

NOTE: By default pricelist rules are selected in order from variant, product, category, global.
As a product can belong to more than one price category, and/or pricelist item the order is indeterminate
in these circumstances.  Therefore it is recommended to use mutually exclusive price categories
within a given pricelist.

Installation
============

There are no special installation instructions for this module.

Configuration
=============

There are no specific mandatory configuration options in this module.  Existing pricelists
will continue to work as expected, however when editing these will need to be converted to the
new many2many fields.

Usage
=====

To use this module, you need to:

#. Open Sales -> Configuration -> Pricing Categories.
#. Click create to create a new category and complete form (self explanatory).
#. It may now be used in pricelists.
#. Pricelist usage is unchanged, except for the addition of fields.

Known issues / Roadmap
======================

* There was a report in past versions, print page in browser is nearly as good now.
* Due to the lack of extensibility of this part of Odoo we overwrite the original function.  This may break other extensions that inherit it.
* Be aware of we hide 'product_id' and 'product_tmpl_id', which in v13 there are 2 onchanges: '_onchange_product_id()', '_onchange_product_tmpl_id()'.
Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/odoonz/sale/issues>`_. In case of trouble, please
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
