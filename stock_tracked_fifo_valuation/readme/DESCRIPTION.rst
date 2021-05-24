This module extends the functionality of `stock_account` to pick the valuation
of in_moves for FIFO valuation only from those available lots on the order.

It will work perfectly in a perfect scenario, whereby the oldest lot is
available in the exact qty shipped, or just 1 lot. Otherwise it falls
back to the default behaviour.

NOTE: V14 is very experimental
