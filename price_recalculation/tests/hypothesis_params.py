# Copyright 2017 Graeme Gellatly
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


PRICE_ARGS = dict(
    min_value=0.10,
    max_value=10000000.0,
    allow_nan=False,
    allow_infinity=False,
)
DISCOUNT_ARGS = dict(
    min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False
)
QTY_ARGS = dict(
    min_value=1.0, max_value=100000.0, allow_nan=False, allow_infinity=False
)
TAX_ARGS = dict(
    min_value=0.01, max_value=1.0, allow_nan=False, allow_infinity=False
)
