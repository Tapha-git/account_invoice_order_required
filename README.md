# Invoice Order Required

Ce module bloque la validation des factures manuelles sans commande liée.

- Facture client (`out_invoice`) : au moins une ligne doit provenir d'une commande de vente.
- Facture fournisseur (`in_invoice`) : au moins une ligne doit provenir d'un bon de commande achat.
- Les utilisateurs du groupe `Autoriser les factures sans bon de commande` peuvent valider les exceptions. Il fautdra activer le mode développeur pour voir la case à cocher.

Le blocage se fait à la validation de la facture, pas à la création du brouillon.
