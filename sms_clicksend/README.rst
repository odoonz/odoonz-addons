=============
SMS ClickSend
=============

Implementation of **ClickSend API** for sending SMS.

This module depends on
https://github.com/OCA/server-tools/tree/19.0/iap_alternative_provider
and provides a new SMS provider ClickSend to replace the one from Odoo SA.

You will also need to install the official ClickSend Python client:
https://pypi.org/project/clicksend-client/

Configuration
=============

To configure this module, you need to:

* Go to Settings > Technical > IAP Accounts
* Create a new account:
    * Provider: SMS ClickSend
    * Company: specify or keep blank for all
    * API Username: your ClickSend username
    * API Key: your ClickSend API key
* SMS are now sent with your ClickSend account.

Which SMS account will be used?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An account defined for a specific company will be chosen over
an account for all companies. So if your installation already has
company-specific SMS accounts (which you don't want to delete) then
you need to create corresponding ClickSend accounts with the same
specific company to override them.
After company specificity, the one with the latest id will be used,
so generally, the above steps are all you need to do.

Balance ignored
~~~~~~~~~~~~~~~

The ClickSend API currently does not get queried for balance.

Fire and forget
~~~~~~~~~~~~~~~

Odoo 18 introduced SMS status tracking and unlike email an SMS is
initially put into "pending" state. We don't do that:
Successfully passing an SMS to the ClickSend API counts as "sent",
no additional querying of the API is done to check the delivery status.

Credits
=======

Authors
~~~~~~~

* MoaHub Limited https://github.com/odoonz
