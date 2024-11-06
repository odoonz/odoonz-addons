=============
SMS ClickSend
=============

Implementation of **ClickSend API** for sending SMS.

This module depends on
https://github.com/OCA/server-tools/tree/16.0/iap_alternative_provider
and provides a new SMS provider ClickSend to replace the one from Odoo SA.

You will also need to install the official ClickSend Python client:
https://pypi.org/project/clicksend-client/

Configuration
=============

To configure this module, you need to:

* Go to Settings > Technical > IAP Accounts
* Create a new account:
    * Provider: SMS ClickSend
    * Service Name: sms
    * Company: specify or keep blank for all
    * API Username: your ClickSend username
    * API Key: your ClickSend API key
* SMS are now sent with your ClickSend account.

Note: An account defined for a specific company will be chosen over
      an account for all companies. So if your installation already has
      company-specific SMS accounts (which you don't want to delete) then
      you need to create corresponding ClickSend accounts with the same
      specific company to override them.

Credits
=======

Authors
~~~~~~~

* MoaHub Limited https://github.com/odoonz
