# -*- coding: utf-8 -*-

from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        self._check_invoice_order_required()
        return super().action_post()

    def _check_invoice_order_required(self):
        if self.env.user.has_group(
            "account_invoice_order_required.group_allow_invoice_without_order"
        ):
            return

        for move in self:
            if move.move_type not in ("out_invoice", "in_invoice"):
                continue

            if move.move_type == "out_invoice" and not move._has_sale_order_source():
                raise UserError(
                    _(
                        "Validation impossible.\n\n"
                        "Cette facture client doit être générée depuis un bon de commande vente.\n"
                        "Veuillez confirmer la commande client puis créer la facture depuis celle-ci."
                    )
                )

            if move.move_type == "in_invoice" and not move._has_purchase_order_source():
                raise UserError(
                    _(
                        "Validation impossible.\n\n"
                        "Cette facture fournisseur doit être générée depuis un bon de commande achat.\n"
                        "Veuillez créer/confirmer le bon de commande puis générer la facture depuis celui-ci."
                    )
                )

    def _has_sale_order_source(self):
        self.ensure_one()
        if self.invoice_origin:
            return True
        return bool(self.line_ids.sale_line_ids)

    def _has_purchase_order_source(self):
        self.ensure_one()
        if self.invoice_origin:
            return True
        if self.line_ids.purchase_line_id:
            return True
        if "purchase_id" in self._fields and self.purchase_id:
            return True
        return False
