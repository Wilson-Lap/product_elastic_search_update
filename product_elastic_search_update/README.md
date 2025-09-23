# API 100p Product Update Module

Ce module permet de synchroniser les informations produits depuis l'API 100p.xcs.be vers Odoo.

## Configuration

### 1. Paramètres Système

Allez dans **Paramètres > Technique > Paramètres > Paramètres système** et configurez :

- `api_100p.base_url` : URL de base de l'API (par défaut: https://api.100p.xcs.be/api/v1)
- `api_100p.bearer_token` : **OBLIGATOIRE** - Votre token d'authentification Bearer
- `api_100p.timeout` : Timeout en secondes pour les appels API (par défaut: 30)
- `api_100p.auto_update_name` : Mettre à jour automatiquement le nom du produit (True/False)
- `api_100p.auto_update_price` : Mettre à jour automatiquement le prix de vente (True/False)
- `api_100p.auto_update_weight` : Mettre à jour automatiquement le poids (True/False)

### 2. Configuration du Token Bearer

**IMPORTANT**: Vous devez configurer votre token Bearer pour que le module fonctionne.

1. Obtenez votre token depuis l'API 100p.xcs.be
2. Allez dans **Paramètres > Technique > Paramètres > Paramètres système**
3. Cherchez la clé `api_100p.bearer_token`
4. Remplacez `YOUR_BEARER_TOKEN_HERE` par votre vrai token

## Utilisation

### Synchronisation Manuelle

1. Allez sur une fiche produit
2. Assurez-vous que le produit a un **code-barres** ou un **numéro d'article API** (api_item_no)
3. Cliquez sur le bouton "**Update from API 100p**" dans l'en-tête

### Synchronisation par Lots

1. Allez dans la liste des produits (**Inventaire > Produits > Produits**)
2. Sélectionnez les produits à synchroniser
3. Utilisez l'action "**Update All Products from API 100p**"

### Synchronisation Automatique

Un cron job peut être activé pour synchroniser automatiquement tous les produits :

1. Allez dans **Paramètres > Technique > Automation > Actions planifiées**
2. Cherchez "**Update Products from API 100p**"
3. Activez la tâche cron
4. Configurez la fréquence (par défaut: quotidienne)

## Champs Synchronisés

Le module synchronise les champs suivants depuis l'API :

| Code API | Champ Odoo | Description |
|----------|------------|-------------|
| F_1 | api_item_no | Numéro d'article |
| F_3 | api_description | Description 1 |
| F_50001 | api_cad_iso | CAD ISO |
| F_80004 | api_dealer_price | Prix revendeur |
| F_80006 | api_date_new_price | Date nouveau prix |
| F_80008 | api_previous_dealer_price | Prix revendeur précédent |
| F_80010 | api_previous_date_new_price | Date précédent nouveau prix |
| C_50000 | api_recupel | Recupel 1 |
| F_42 | api_net_weight | Poids net |
| F_41 | api_gross_weight | Poids brut |
| C_50010 | api_energy_class | Classe énergétique |
| F_47 | api_tariff_no | Numéro tarifaire |
| F_54 | api_blocked | Bloqué |

### Mise à Jour Automatique des Champs Standard

Si configuré, le module peut aussi mettre à jour automatiquement :
- **Nom du produit** (depuis api_description)
- **Prix de vente** (depuis api_dealer_price)  
- **Poids** (depuis api_net_weight)

## Suivi des Synchronisations

Chaque produit dispose de champs de suivi :
- **api_last_sync** : Date de dernière synchronisation
- **api_sync_status** : Statut (Success/Error/Never Synced)
- **api_sync_message** : Message d'erreur si applicable

### Filtres Disponibles

Dans la liste des produits, vous pouvez filtrer par :
- Synchronisation réussie
- Erreur de synchronisation
- Jamais synchronisé
- Articles bloqués par l'API

## Résolution des Problèmes

### Erreur "Bearer token not configured"
- Configurez le paramètre système `api_100p.bearer_token`

### Erreur "No barcode or item number found"
- Assurez-vous que le produit a un code-barres ou un numéro d'article API

### Erreur de connexion API
- Vérifiez votre connexion internet
- Vérifiez que l'URL de l'API est correcte
- Vérifiez que votre token Bearer est valide

### Erreur "Invalid JSON response"
- L'API peut être temporairement indisponible
- Contactez le support de l'API 100p.xcs.be

## Format de Réponse API Attendu

Le module attend une réponse JSON de ce format :

```json
{
    "status": "success",
    "message": "Article found with article number \"12441114\"",
    "data": {
        "F_54": "No",
        "F_80010": "20/06/2022",
        "F_42": "300",
        "F_41": "425",
        "F_80006": "15/09/2023",
        "F_80008": "279,22",
        "F_47": "94009329",
        "F_80004": "268,72",
        "F_50001": "BH_30_LED_G10.PNG",
        "F_1": "12441114",
        "F_3": "5H30-IP20-LG10-CRI97-9,1W-4K-BM45°-RFL-WHT-ID0350MADC(1-10V)",
        "C_50010": "F",
        "C_50000": "5.6"
    }
}
```

## Logs

Les logs du module sont disponibles dans les logs Odoo avec le préfixe `product_elastic_search_update`.
