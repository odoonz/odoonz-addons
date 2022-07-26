.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================================
Microsoft Graph Oauth Authentication
====================================

*IMPORTANT NOTE: There are reports of this module working on v15 untouched, however no use or testing by author as skipping v15*

Allows users to login using Microsoft Graph in Azure AD environments.
It is fairly naive, and just tests if the oauth provider is graph.microsoft.com and if so modifies the oauth request.

Installation
============

There are no special installation instructions for this module.

Configuration
=============

If using B2B authentication you will need to populate users authentication usernames and choose an Oauth provider manually. You will also need to invite the user to "reset" password and instruct them to use the Oauth button to login the first time (details below).

Step 1 - The configuration in Azure Portal

- Go to portal.azure.com > App Registrations > New Registration
- Enter a name for registration e.g My Odoo System - Oauth
- Choose "Accounts in this organizational directory only" (Single tenant)
- In Redirect URI, set as following while replacing with Odoo domain: https://<yourodoopublicdomain>/auth_oauth/signin
- Click [Register] button
- Go to API permissions > Add a permission and follow these steps to set "Delegated permissions" for MS Graph
	- Required permissions for Microsoft Graph: Directory.AccessAsUser.All, email, openid, profile, User.Read
	- Click "Grant admin content for [mycompany]" button
- EITHER go to Authentication tab and under "Implicit grant and hybrid flows" choose "Access tokens (used for implicit flows)" OR manually edit manifest to set "oauth2AllowImplicitFlow": true
- Ensure redirect URL is set as https://<yourodoopublicdomain>/auth_oauth/signin
- Whilst in Azure portal, make a copy of the "Application (client) ID" and your "Directory (tenant) ID" in a text document - You need these next in Odoo

Step 2 - Odoo config of OAuth provider

- Go to Settings > Users & Companies > OAuth Providers
- Create a new provider and enter details below.
- Provider name: AzureAD
- Client ID: <Client ID provided when registering Application> from before
- Login button label: Login with Microsoft
- Auth URL - Replace the placeholder with your directory tenant ID from before: https://login.microsoftonline.com/<yourdirectorytenantid>/oauth2/v2.0/authorize
- Scope: User.Read User.ReadBasic.All
- UserInfo URL: https://graph.microsoft.com/v1.0/me
- Data Endpoint: <Empty>

Step 3 - User Signup

- Go to Settings > Users & Companies
- Choose a user and in the Oauth tab, set the provider as AzureAD
- Next click "Send Password Reset Instructions" which will email the user
- Instruct the user to NOT SET A PASSWORD, but instead click on the [Login with Microsoft] button after following the link in the email
- User completes the steps to link Azure and Odoo accounts
- Repeat for all users

*IMPORTANT NOTE: After setting up users with Oauth, it is advised as Admin to manually change their passwords to a complex randomly generated PW (at least 20 chars) and never log it down.
The user will instead be forced to use Oauth as their login method. If you neglect to do this the user will still be able to login with passwords.*

If you like to enable user to signup themselves, just turn on the B2C login in odoo - setting - Users - Customer Account

Usage
=====

- User goes to standard Odoo login screen
- Chooses [Login with Microsoft] and authentication happens automatically with no password

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
