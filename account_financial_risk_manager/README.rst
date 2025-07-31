==============================
Account Financial Risk Manager
==============================

This module extends the functionality of OCA Financial Risk modules by adding
a separate security group for credit controllers rather than requiring
accounting access to release orders. It provides comprehensive credit risk
management tools including bulk credit limit management and enhanced risk
computation.

**Table of contents**

.. contents::
   :local:

Features
========

* **Security Groups**: Separate security groups for credit risk management
  * Risk Manager (Edit Risk): Can view risk limits and override partner risk exceptions
  * User (readonly): Read-only access to risk information

* **Bulk Credit Management**: Wizard for setting credit limits on multiple customers
  * Set overall credit limits
  * Configure overdue invoices limits
  * Define credit policies
  * Bulk apply to selected companies

* **Enhanced Partner Views**: 
  * Search filter for partners with no credit limit
  * Risk management fields with proper access controls

* **Sale Order Risk Computation**: 
  * Enhanced risk calculation that considers force invoiced orders
  * Excludes force invoiced orders from risk calculations

* **Access Control**: 
  * Field-level security for risk-related fields
  * Proper permission management for credit controllers

Usage
=====

Security Groups
---------------

To use this module, you need to add users to the appropriate security groups:

* **Risk Manager (Edit Risk)**: For users who need to manage credit limits and override risk exceptions
* **User (readonly)**: For users who only need to view risk information

Bulk Credit Limit Management
----------------------------

1. Go to **Contacts** and select multiple company partners
2. Use the **Set Customer Risk** action from the action menu
3. Configure the following settings:
   * **Overall Credit Limit**: Total credit limit for the partner
   * **Overdue Invoices Limit**: Maximum allowed overdue amount
   * **Credit Policy**: Policy description or notes
4. Click **Set Limits** to apply to all selected partners

The wizard will automatically:
* Enable all risk inclusion flags
* Apply settings only to company partners (not contacts)
* Skip parent companies to avoid conflicts

Risk Computation
----------------

The module enhances risk computation for sale orders by:
* Excluding force invoiced orders from risk calculations
* Providing more accurate risk assessment
* Maintaining compatibility with existing financial risk modules

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/odoonz/odoonz-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
`feedback <https://github.com/odoonz/odoonz-addons/issues/new?body=module:%20account_financial_risk_manager%0Aversion:%2018.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Graeme Gellatly

Contributors
~~~~~~~~~~~~

* Graeme Gellatly <graeme@moahub.nz> (https://moahub.nz)

Maintainers
~~~~~~~~~~~

This module is maintained by the MoaHub.

.. image:: https://odoo-community.org/logo.png
   :alt: MoaHub Ltd
   :target: https://moahub.nz
