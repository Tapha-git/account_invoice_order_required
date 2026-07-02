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
        if self.line_ids.sale_line_ids:
            return True
        return bool(self._matching_origin_orders("sale.order"))

    def _has_purchase_order_source(self):
        self.ensure_one()
        if self.line_ids.purchase_line_id:
            return True
        if "purchase_id" in self._fields and self.purchase_id:
            return True
        return bool(self._matching_origin_orders("purchase.order"))

    def _origin_names(self):
        self.ensure_one()
        if not self.invoice_origin:
            return []
        return [
            origin.strip()
            for origin in self.invoice_origin.replace(";", ",").split(",")
            if origin.strip()
        ]

    def _matching_origin_orders(self, model_name):
        self.ensure_one()
        origins = self._origin_names()
        if not origins or model_name not in self.env:
            return self.env[model_name]

        orders = self.env[model_name].search([
            ("name", "in", origins),
            ("company_id", "in", [False, self.company_id.id]),
        ])
        return orders.filtered(lambda order: self._same_commercial_partner(order))

    def _same_commercial_partner(self, order):
        self.ensure_one()
        invoice_partner = self.partner_id.commercial_partner_id
        candidate_partners = order.partner_id.commercial_partner_id
        if "partner_invoice_id" in order._fields and order.partner_invoice_id:
            candidate_partners |= order.partner_invoice_id.commercial_partner_id
        return invoice_partner in candidate_partners
