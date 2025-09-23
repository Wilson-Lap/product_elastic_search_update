#!/usr/bin/env python3
"""
Script d'exemple pour tester l'API 100p.xcs.be

Usage:
    python test_api_call.py YOUR_BEARER_TOKEN 12441114
"""

import sys
import requests
import json


def test_api_call(bearer_token, article_number):
    """Test l'appel à l'API 100p.xcs.be"""
    
    url = f"https://api.100p.xcs.be/api/v1/articles/{article_number}"
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    try:
        print(f"Calling API: {url}")
        print(f"Headers: {headers}")
        print("-" * 50)
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        print("Response Status Code:", response.status_code)
        print("Response JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        if data.get('status') == 'success' and 'data' in data:
            print("\n" + "=" * 50)
            print("PARSED DATA:")
            print("=" * 50)
            
            api_data = data['data']
            field_descriptions = {
                'F_1': 'Item No.',
                'F_3': 'Description 1',
                'F_50001': 'CAD ISO',
                'F_80004': 'Dealer Price',
                'F_80006': 'Date New Price',
                'F_80008': 'Previous Dealer Price',
                'F_80010': 'Previous Date New Price',
                'C_50000': 'Recupel 1',
                'F_42': 'Net Weight',
                'F_41': 'Gross Weight',
                'C_50010': 'Energy Class',
                'F_47': 'Tariff No.',
                'F_54': 'Blocked'
            }
            
            for field_code, description in field_descriptions.items():
                if field_code in api_data:
                    print(f"{field_code} ({description}): {api_data[field_code]}")
                else:
                    print(f"{field_code} ({description}): NOT FOUND")
        else:
            print(f"\nAPI Error: {data.get('message', 'Unknown error')}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_api_call.py YOUR_BEARER_TOKEN ARTICLE_NUMBER")
        print("Example: python test_api_call.py abc123xyz 12441114")
        sys.exit(1)
    
    bearer_token = sys.argv[1]
    article_number = sys.argv[2]
    
    test_api_call(bearer_token, article_number)
