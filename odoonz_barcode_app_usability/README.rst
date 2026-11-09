=====================
Barcode App Usability
=====================

Hold an Inventory Count for review from the barcode app.

Counted lines are marked **Awaiting Review** when the user scans the
review barcode, and when they press **Wait a Review** on the Inventory
Count confirmation. Applying the count clears the flag.

The Inventory Adjustments list has a **To Review** filter for those
quants.

Scanning a transfer also finds the open transfer that follows it. A
pick is printed before the pack exists, so the slip carries the pick
number. Once the pack exists, scanning that number from the barcode
home screen, or from the pack operation, opens the pack.

Usage
=====

#. Open the barcode app and start an Inventory Count.
#. Count the lines.
#. Scan the review command, or press **Wait a Review** on the
   confirmation dialog.
#. Find the quants later with Inventory Adjustments → To Review.
#. Applying the count clears Awaiting Review.

Scanning the previous transfer
==============================

#. Print the pick. Its barcode is the pick number.
#. Validate the pick. That creates the pack.
#. From the barcode home screen, or from the pack operation, scan the
   pick number. The open pack opens. An in-progress pick still opens
   itself.

Transfer name matching ignores letter case, so a USB keyboard-wedge
scanner with Caps Lock on still opens the pick or the pack that follows
it.

Changelog
=========

19.0.1.2.0 (2026-11-10)
-----------------------

* Match transfer names case-insensitively when scanning a pick document
  or the prior transfer (Caps Lock on a USB scanner).

19.0.1.1.0 (2026-11-03)
-----------------------

* A barcode scan finds the open transfer whose previous transfer is the
  scanned number.

19.0.1.0.0 (2026-10-29)
-----------------------

* Initial release.
