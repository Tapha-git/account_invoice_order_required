# Invoice Order Required

Addon Odoo 18 qui bloque la validation des factures manuelles sans commande liée.

- Facture client (`out_invoice`) : au moins une ligne doit provenir d'une commande de vente.
- Facture fournisseur (`in_invoice`) : au moins une ligne doit provenir d'un bon de commande achat.
- Les utilisateurs du groupe `Autoriser les factures sans bon de commande` peuvent valider les exceptions.

Le blocage se fait à la validation de la facture, pas à la création du brouillon.
