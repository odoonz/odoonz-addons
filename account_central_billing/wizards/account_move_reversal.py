from odoo import models


class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """

    _inherit = "account.move.reversal"

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res.update(
            {
                "order_partner_id": move.order_partner_id.id,
                "order_invoice_id": move.order_invoice_id.id,
            }
        )
        return res
