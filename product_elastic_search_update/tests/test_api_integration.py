from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from unittest.mock import patch, MagicMock


class TestAPI100pIntegration(TransactionCase):

    def setUp(self):
        super().setUp()
        self.product = self.env['product.template'].create({
            'name': 'Test Product',
            'barcode': '12441114',
            'list_price': 100.0,
        })

        self.env['ir.config_parameter'].sudo().set_param('api_100p.base_url', 'https://api.100p.xcs.be/api/v1')
        self.env['ir.config_parameter'].sudo().set_param('api_100p.bearer_token', 'test_token')

    def test_get_api_config(self):
        config = self.product._get_api_config()
        self.assertEqual(config['base_url'], 'https://api.100p.xcs.be/api/v1')
        self.assertEqual(config['bearer_token'], 'test_token')

    @patch('requests.get')
    def test_call_api_100p_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "success",
            "message": "Article found",
            "data": {
                "F_1": "12441114",
                "F_3": "Test Description",
                "F_80004": "268.72",
                "F_42": "300",
                "F_54": "No"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = self.product._call_api_100p('12441114')

        self.assertEqual(result['F_1'], '12441114')
        self.assertEqual(result['F_3'], 'Test Description')
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_call_api_100p_error(self, mock_get):
        mock_get.side_effect = Exception("Connection error")
        
        with self.assertRaises(UserError):
            self.product._call_api_100p('12441114')

    def test_update_from_api_data(self):
        api_data = {
            "F_1": "12441114",
            "F_3": "Test Description from API",
            "F_80004": "268.72",
            "F_42": "300",
            "F_41": "425",
            "F_54": "No",
            "C_50010": "F"
        }
        
        values = self.product._update_from_api_data(api_data)

        self.assertEqual(values['api_item_no'], '12441114')
        self.assertEqual(values['api_description'], 'Test Description from API')
        self.assertEqual(values['api_dealer_price'], 268.72)
        self.assertEqual(values['api_net_weight'], 300.0)
        self.assertEqual(values['api_gross_weight'], 425.0)
        self.assertEqual(values['api_blocked'], False)
        self.assertEqual(values['api_energy_class'], 'F')
        self.assertEqual(values['api_sync_status'], 'success')

    @patch('odoo.addons.product_elastic_search_update.models.product_template.ProductTemplate._call_api_100p')
    def test_action_update_from_api_100p(self, mock_call_api):
        """Test de l'action de mise à jour complète"""
        # Mock des données API
        mock_call_api.return_value = {
            "F_1": "12441114",
            "F_3": "Updated Description",
            "F_80004": "300.00",
            "F_42": "250"
        }

        self.product.action_update_from_api_100p()

        self.assertEqual(self.product.api_item_no, '12441114')
        self.assertEqual(self.product.api_description, 'Updated Description')
        self.assertEqual(self.product.api_dealer_price, 300.0)
        self.assertEqual(self.product.api_net_weight, 250.0)
        self.assertEqual(self.product.api_sync_status, 'success')
        self.assertTrue(self.product.api_last_sync)

    def test_action_update_no_barcode(self):
        product_no_barcode = self.env['product.template'].create({
            'name': 'Product without barcode',
        })
        
        with self.assertRaises(UserError):
            product_no_barcode.action_update_from_api_100p()

    def test_missing_bearer_token(self):
        self.env['ir.config_parameter'].sudo().set_param('api_100p.bearer_token', '')
        
        with self.assertRaises(UserError):
            self.product._call_api_100p('12441114')

    @patch('odoo.addons.product_elastic_search_update.models.product_template.ProductTemplate.action_update_from_api_100p')
    def test_cron_update_products(self, mock_update):
        product2 = self.env['product.template'].create({
            'name': 'Test Product 2',
            'barcode': '12345678',
        })

        self.env['product.template'].cron_update_products_from_api()

        self.assertEqual(mock_update.call_count, 2)
