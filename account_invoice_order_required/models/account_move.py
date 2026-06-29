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

            invoice_lines = move.invoice_line_ids.filtered(lambda line: not line.display_type)
            if move.move_type == "out_invoice" and not self._has_sale_order_line(invoice_lines):
                raise UserError(
                    _(
                        "Validation impossible.\n\n"
                        "Cette facture client doit être générée depuis un bon de commande vente.\n"
                        "Veuillez confirmer la commande client puis créer la facture depuis celle-ci."
                    )
                )

            if move.move_type == "in_invoice" and not self._has_purchase_order_line(invoice_lines):
                raise UserError(
                    _(
                        "Validation impossible.\n\n"
                        "Cette facture fournisseur doit être générée depuis un bon de commande achat.\n"
                        "Veuillez créer/confirmer le bon de commande puis générer la facture depuis celui-ci."
                    )
                )

    @staticmethod
    def _has_sale_order_line(invoice_lines):
        return any(line.sale_line_ids for line in invoice_lines)

    @staticmethod
    def _has_purchase_order_line(invoice_lines):
        return any(line.purchase_line_id for line in invoice_lines)
