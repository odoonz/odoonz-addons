.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================================
Microsoft Graph Oauth Authentication
====================================

Allows users to login using Microsoft Graph in Azure AD environments.
This module is experimental and somewhat untested.


Installation
============

There are no special installation instructions for this module.

Configuration
=============

If using B2B authentication you will need to populate users
authentication usernames and complete an oauth provider.

Provider name: AzureAD
Client ID: Client ID provided when registering Application
Body: Login with Microsoft
Auth URL: https://login.microsoftonline.com/common/oauth2/v2.0/authorize
Scope: User.Read User.ReadBasic.All
Validation URL: https://graph.microsoft.com/v1.0/me

Usage
=====

User select Login with Microsoft at login screen to authenticate.

Known issues / Roadmap
======================

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/odoonz/account/issues>`_. In case of trouble, please
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
