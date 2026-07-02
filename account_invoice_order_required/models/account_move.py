# -*- coding: utf-8 -*-

import re

from markupsafe import Markup

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import html2plaintext


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
        if self.line_ids.sale_line_ids:
            return True
        if self._source_document_has_order_reference(("S", "SO")):
            return True
        return bool(self._matching_origin_orders("sale.order"))

    def _has_purchase_order_source(self):
        self.ensure_one()
        if self.invoice_origin:
            return True
        if self.line_ids.purchase_line_id:
            return True
        if "purchase_id" in self._fields and self.purchase_id:
            return True
        if self._source_document_has_order_reference(("P", "PO", "PUR", "RFQ")):
            return True
        return bool(self._matching_origin_orders("purchase.order"))

    def _source_document_has_order_reference(self, prefixes):
        """Check the visible Source Document field before using chatter fallback."""
        self.ensure_one()
        source_document = self.invoice_origin or ""
        if not source_document:
            return False
        references = self._extract_order_references(source_document)
        return any(
            reference.upper().startswith(tuple(prefix.upper() for prefix in prefixes))
            for reference in references
        )

    def _origin_names(self):
        """Return normalized source document names from invoice metadata.

        Besides ``invoice_origin``, Odoo may only keep the source purchase order
        in the chatter, e.g. "Cette facture fournisseur a été créée depuis :P00250".
        """
        self.ensure_one()
        origins = set()
        origins.update(self._extract_origin_names(self.invoice_origin or ""))

        for message in self.sudo().message_ids:
            html_body = str(Markup(message.body or "").unescape())
            text_body = html2plaintext(html_body)
            origins.update(self._extract_origin_names(html_body))
            origins.update(self._extract_origin_names(text_body))

        return list(origins)

    @staticmethod
    def _extract_origin_names(text):
        origins = set()
        if not text:
            return origins

        for raw_origin in re.split(r"[,;\n]+", text):
            origin = raw_origin.strip().lstrip(":").strip()
            if not origin:
                continue

            candidates = {
                origin,
                re.sub(r"\s*\([^)]*\)\s*$", "", origin).strip(),
            }

            source_match = re.search(
                r"(?:depuis|from)\s*:?\s*([A-Za-z0-9][A-Za-z0-9_./-]*)",
                origin,
                flags=re.IGNORECASE,
            )
            if source_match:
                candidates.add(source_match.group(1).strip())

            candidates.update(self._extract_order_references(origin))

            for candidate in candidates:
                candidate = candidate.strip().strip(":")
                if not candidate:
                    continue
                origins.add(candidate)
                first_token = candidate.split()[0].strip(":")
                if first_token:
                    origins.add(first_token)

        return origins

    @staticmethod
    def _extract_order_references(text):
        return re.findall(
            r"\b(?:PO|PUR|RFQ|SO|P|S)\d{2,}\b",
            text or "",
            flags=re.IGNORECASE,
        )

    def _matching_origin_orders(self, model_name):
        self.ensure_one()
        origins = self._origin_names()
        if not origins or model_name not in self.env:
            return self.env[model_name]

        Order = self.env[model_name].sudo()
        orders = Order.search([
            ("name", "in", origins),
            ("company_id", "in", [False, self.company_id.id]),
        ])
        if not orders:
            orders = Order.search([
                ("name", "in", origins),
            ])
        return orders
