from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    api_item_no = fields.Char(string='Item No. (F_1)', help='Article number from API')
    api_description = fields.Text(string='Description 1 (F_3)', help='Description from API')
    api_cad_iso = fields.Char(string='CAD ISO (F_50001)', help='CAD ISO from API')
    api_dealer_price = fields.Float(string='Dealer Price (F_80004)', help='Current dealer price from API')
    api_date_new_price = fields.Datetime(string='Date New Price (F_80006)', help='Date of new price from API')
    api_previous_dealer_price = fields.Float(string='Previous Dealer Price (F_80008)', help='Previous dealer price from API')
    api_previous_date_new_price = fields.Datetime(string='Previous Date New Price (F_80010)', help='Previous date new price from API')
    api_recupel = fields.Char(string='Recupel 1 (C_50000)', help='Recupel information from API')
    api_net_weight = fields.Float(string='Net Weight (F_42)', help='Net weight from API')
    api_gross_weight = fields.Float(string='Gross Weight (F_41)', help='Gross weight from API')
    api_energy_class = fields.Char(string='Energy Class (C_50010)', help='Energy class from API')
    api_tariff_no = fields.Char(string='Tariff No. (F_47)', help='Tariff number from API')
    api_blocked = fields.Boolean(string='Blocked (F_54)', help='Article is blocked/unavailable')
    hundred_p_article_reference = fields.Char(string='100p Article Reference', help='Reference number for 100p product')

    api_last_sync = fields.Datetime(string='Last API Sync', help='Last synchronization with API')
    api_sync_status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error'),
        ('never', 'Never Synced')
    ], string='API Sync Status', default='never')
    api_sync_message = fields.Text(string='Sync Message', help='Last sync message or error')

    @api.model
    def _get_api_config(self):

        ICPSudo = self.env['ir.config_parameter'].sudo()
        return {
            'base_url': ICPSudo.get_param('api_100p.base_url', 'https://api.100p.xcs.be/api/v1'),
            'bearer_token': ICPSudo.get_param('api_100p.bearer_token', ''),
        }

    def _call_api_100p(self, article_number):

        config = self._get_api_config()
        
        if not config['bearer_token']:
            raise UserError(_("Bearer token not configured. Please set 'api_100p.bearer_token' system parameter."))
        
        url = f"{config['base_url']}/articles/{article_number}"
        headers = {
            'Authorization': f'Bearer {config["bearer_token"]}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            _logger.info(f"Calling API 100p for article: {article_number}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success' and 'data' in data:
                return data['data']
            else:
                raise UserError(_("API returned unsuccessful status: %s") % data.get('message', 'Unknown error'))
                
        except requests.exceptions.RequestException as e:
            _logger.error(f"API call failed for article {article_number}: {str(e)}")
            raise UserError(_("Failed to connect to API: %s") % str(e))
        except json.JSONDecodeError as e:
            _logger.error(f"Invalid JSON response for article {article_number}: {str(e)}")
            raise UserError(_("Invalid JSON response from API"))

    def _update_from_api_data(self, api_data):
        field_mapping = {
            'F_1': 'api_item_no',
            'F_3': 'api_description', 
            'F_50001': 'api_cad_iso',
            'F_80004': 'api_dealer_price',
            'F_80006': 'api_date_new_price',
            'F_80008': 'api_previous_dealer_price',
            'F_80010': 'api_previous_date_new_price',
            'C_50000': 'api_recupel',
            'F_42': 'api_net_weight',
            'F_41': 'api_gross_weight',
            'C_50010': 'api_energy_class',
            'F_47': 'api_tariff_no',
            'F_54': 'api_blocked'
        }
        
        values = {}
        
        for api_field, odoo_field in field_mapping.items():
            if api_field in api_data:
                api_value = api_data[api_field]

                if odoo_field in ['api_dealer_price', 'api_previous_dealer_price', 'api_net_weight', 'api_gross_weight']:
                    try:
                        values[odoo_field] = float(api_value) if api_value else 0.0
                    except (ValueError, TypeError):
                        values[odoo_field] = 0.0
                        
                elif odoo_field in ['api_date_new_price', 'api_previous_date_new_price']:
                    if api_value:
                        try:
                            from datetime import datetime
                            if '/' in str(api_value):
                                values[odoo_field] = datetime.strptime(str(api_value), '%d/%m/%Y')
                            else:
                                values[odoo_field] = api_value
                        except ValueError:
                            _logger.warning(f"Invalid date format for {api_field}: {api_value}")
                            values[odoo_field] = False
                    else:
                        values[odoo_field] = False
                        
                elif odoo_field == 'api_blocked':
                    values[odoo_field] = bool(api_value) if api_value else False
                    
                else:
                    # Champs texte
                    values[odoo_field] = str(api_value) if api_value else ''

        values.update({
            'api_last_sync': fields.Datetime.now(),
            'api_sync_status': 'success',
            'api_sync_message': _('Successfully updated from API')
        })
        
        # Optionnel: mettre à jour aussi certains champs standard d'Odoo
        if 'api_description' in values and values['api_description']:
            values['name'] = values['api_description']
        
        if 'api_dealer_price' in values and values['api_dealer_price']:
            values['list_price'] = values['api_dealer_price']
            
        if 'api_net_weight' in values and values['api_net_weight']:
            values['weight'] = values['api_net_weight']

        # Ajouter la catégorie "100 % Light" pour les produits synchronisés depuis l'API
        category_100p_light = self.env.ref('product_elastic_search_update.product_category_100p_light', raise_if_not_found=False)
        if category_100p_light:
            values['categ_id'] = category_100p_light.id

        return values

    def action_update_from_api_100p(self):
        for record in self:
            try:
                article_number = record.hundred_p_article_reference or record.api_item_no
                
                if not article_number:
                    raise UserError(_("No barcode or item number found for product '%s'") % record.name)

                api_data = record._call_api_100p(article_number)

                values = record._update_from_api_data(api_data)
                record.write(values)
                
                _logger.info(f"Successfully updated product {record.name} from API 100p")
                
            except Exception as e:
                _logger.error(f"Failed to update product {record.name}: {str(e)}")
                record.write({
                    'api_last_sync': fields.Datetime.now(),
                    'api_sync_status': 'error',
                    'api_sync_message': str(e)
                })
                raise

    @api.model
    def cron_update_products_from_api(self):
        products = self.search([('barcode', '!=', False)])
        
        success_count = 0
        error_count = 0
        
        for product in products:
            try:
                product.action_update_from_api_100p()
                success_count += 1
            except Exception as e:
                error_count += 1
                _logger.error(f"Cron update failed for product {product.name}: {str(e)}")
        
        _logger.info(f"API sync completed: {success_count} success, {error_count} errors")
        
        return True
