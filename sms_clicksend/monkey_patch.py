# Replace Odoo's SmsApi with our custom implementation
# (it is no longer a model in the env)


import importlib

from odoo.addons.sms.models import sms_sms
from odoo.addons.sms.tools import sms_api

from .tools.sms_api import ClicksendSmsApi

sms_api.SmsApi = ClicksendSmsApi
importlib.reload(sms_sms)
