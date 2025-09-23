{
    "name": "API 100p Product Update",
    "version": "17.1",
    "category": "Inventory",
    "summary": "Update product information from API 100p.xcs.be",
    "description": """
        This module allows to update product information from the API 100p.xcs.be
        using the product barcode or item number.
        
        Features:
        - Automatic synchronization of product data from API 100p.xcs.be
        - Support for all API fields (F_1, F_3, F_50001, etc.)
        - Manual and automatic update capabilities  
        - Sync status tracking and error handling
        - Configurable field mapping and auto-update options
        
        API Fields Supported:
        - F_1: Item Number
        - F_3: Description
        - F_50001: CAD ISO
        - F_80004: Dealer Price
        - F_80006: Date New Price
        - F_80008: Previous Dealer Price
        - F_80010: Previous Date New Price
        - C_50000: Recupel
        - F_42: Net Weight
        - F_41: Gross Weight
        - C_50010: Energy Class
        - F_47: Tariff Number
        - F_54: Blocked Status
    """,
    "author": "Lapinski Sebastian",
    "depends": ["base", "product", "stock"],
    "external_dependencies": {
        "python": ["requests"]
    },
    "data": [
        "data/product_category_data.xml",
        "views/product_template_views.xml",
        "data/system_parameters.xml",
        "data/cron_jobs.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}