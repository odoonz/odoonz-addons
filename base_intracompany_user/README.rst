======================
Base Intracompany User
======================

New "Intracompany User" for executing actions restricted to a single company. The use case is usually
within automation or company specific things that need to be from a company restricted user.

Configuration
=============

Assign to this company field a user that is only in that company.

Usage
=====

In your code, use `.with_user(some_company.intracompany_user)`.

Changelog
=========
