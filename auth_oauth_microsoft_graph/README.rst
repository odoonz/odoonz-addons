.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================================
Microsoft Graph Oauth Authentication
====================================

Allows users to login using Microsoft Graph in Azure AD environments.
It is fairly naive, and just tests if the oauth provider is graph.microsoft.com
and if so modifies the oauth request.


Installation
============

There are no special installation instructions for this module.

Configuration
=============

If using B2B authentication you will need to populate users
authentication usernames and complete an oauth provider.

- Provider name: AzureAD
- Client ID: <Client ID provided when registering Application>
- Body: Login with Microsoft
- Auth URL: https://login.microsoftonline.com/common/oauth2/v2.0/authorize
- Scope: User.Read User.ReadBasic.All
- Validation URL: https://graph.microsoft.com/v1.0/me
- Data URL: <Empty>

The configuration in Azure APP:

- Enable multi-tenanted in Azure App - setting - properties
- Required permissions - Windows Azure Active Directory - Grant permissions - Sign in and read user profile, Sign in and read user profile , Access the directory as the signed-in user
- Required permissions - Microsoft Graph - Grant permissions - Access the directory as the signed-in user, Sign users in , View users' email address
- Edit manifest - "oauth2AllowImplicitFlow": true,
- Redirect URL: https://<yourodoopublicdomain>/auth_oauth/signin

If you like to enable user to signup, just turn on the B2C login in odoo - setting - Users - Customer Account

Usage
=====

- Prior to first login, user must exist in Odoo if signup not enabled. You must also "Send an invitation" to reset password which user must complete.
- User selects Login with Microsoft at login screen to authenticate.

Known issues / Roadmap
======================

Ideally this module shouldn't be required and will be deprecated
as soon as Odoo supports AZUREAD logins.

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
* Chris Mann <https://github.com/chrisandrewmann>

Maintainer
----------

This module is maintained by Open for Small Business Ltd.

Open for Small Business is a small developer and integrator of Odoo software since 2009.
