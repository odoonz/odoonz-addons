from dateutil.relativedelta import relativedelta
from odoo import fields

PRETTY_DATETIME_FORMAT = '%a %d %b %Y %H:%M'


def adjust_date(date_string, **kwargs):
    '''
    Increments a date string by the amount requested
    kwargs are expected to be kwargs suitable for use by relativedelta
    e.g. days, weeks, months, years, hours, minutes, seconds
    '''
    return fields.Date.to_string(
        fields.Date.from_string(date_string) + relativedelta(**kwargs))


def adjust_datetime(date_string, **kwargs):
    return fields.Datetime.to_string(
        fields.Datetime.from_string(date_string) + relativedelta(**kwargs))


fields.Date.adjust_date = adjust_date
fields.Datetime.adjust_datetime = adjust_datetime
