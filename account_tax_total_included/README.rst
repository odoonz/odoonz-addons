Account Tax Total Included
==========================

This module automatically applies tax total included mode based on partner settings, eliminating the need for manual button clicks on invoices.

Features
--------

* **Partner-level Configuration**: Set GST Inclusive flag on partners to automatically apply tax total included mode to all their invoices
* **Automatic Inheritance**: Invoices automatically inherit the tax inclusive setting from their partner
* **Real-time Updates**: Changes to partner settings automatically update existing draft invoices
* **Seamless Integration**: Works transparently with existing tax computation logic

How it Works
------------

1. **Partner Configuration**: Set the "GST Inclusive" flag on any partner in the Sales & Purchases tab
2. **Automatic Application**: All invoices created for that partner automatically use tax total included mode
3. **Dynamic Updates**: Changing the partner setting immediately updates all draft invoices
4. **Tax Computation**: Taxes are computed using the `total_included` special mode when enabled

Technical Details
----------------

* **Partner Model**: `res.partner` extended with `force_tax_total_included` field
* **Invoice Model**: `account.move` automatically inherits the setting from the partner
* **Tax Computation**: `account.tax` uses `special_mode = 'total_included'` when enabled
* **Automatic Updates**: Partner changes trigger immediate invoice updates

Usage
-----

1. Go to any partner form
2. Navigate to the Sales & Purchases tab
3. Set the "GST Inclusive" checkbox
4. All future invoices for this partner will automatically use tax total included mode
5. Existing draft invoices are automatically updated

Benefits
--------

* **Eliminates Manual Work**: No more clicking buttons on individual invoices
* **Consistent Behavior**: All invoices for a partner automatically use the same tax mode
* **Bulk Updates**: Change partner setting once, affects all invoices
* **User Experience**: Cleaner invoice interface without unnecessary buttons

Migration from Previous Version
------------------------------

The previous version used buttons on invoices to toggle tax modes. This version:
* Removes the toggle buttons
* Moves the logic to partner level
* Automatically applies settings to all invoices
* Maintains backward compatibility for existing data

