========================
Stock Barcode Lot Prompt
========================

Use this on barcode Inventory Count when products are tracked by lot or
serial number, and those numbers can be read but not scanned.

A product barcode carries no lot. Inventory Count would otherwise have
no lot to store. This module keeps the scan on the main list and asks
for a lot before a quant is saved, so a tracked product is never counted
without one.

Use case
========

The goods have a product barcode, and a lot or serial name printed on
the pack, coil, or label. That name is not a barcode. You still want to
count stock in Odoo Inventory: scan the product, then look up the
existing lot or type the name and create it.

Usage
=====

#. Open Inventory Count.
#. Scan a location when the screen asks for one.
#. Scan a product tracked by lots or serial numbers.
#. Search for an existing lot, or type a new name and choose Create.
#. Scan the same product again to count another lot. Each lot is its own line.
#. Cancel drops the prompt and does not create a quant.

Scanning the product barcode again asks for a lot again. It does not add
quantity to a lot already on the count.

Untracked products, and scans that already include a lot, are unchanged.


Changelog
=========
