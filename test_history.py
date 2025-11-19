#!/usr/bin/env python3
"""
Test script to check history endpoints
"""

import requests
import json

# Test data - corrected ports based on startup logs
BASE_URLS = {
    'url_summarizer': 'http://localhost:8002',
    'file_service': 'http://localhost:8001', 
    'comparison_service': 'http://localhost:8003',
    'summarization_backend': 'http://localhost:8004',
    'auth_service': 'http://localhost:8000'
}

def test_endpoint(service_name, endpoint, method='GET', headers=None, data=None):
    """Test an endpoint and return response"""
    url = f"{BASE_URLS[service_name]}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        else:
            response = requests.request(method, url, headers=headers, json=data)
            
        print(f"\n=== {service_name.upper()} - {method} {endpoint} ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response
        
    except requests.exceptions.ConnectionError as e:
        print(f"\n=== {service_name.upper()} - CONNECTION ERROR ===")
        print(f"Cannot connect to {url}")
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"\n=== {service_name.upper()} - ERROR ===")
        print(f"Error: {e}")
        return None

def main():
    print("🧪 Testing History Endpoints...")
    
    # Test basic connectivity
    print("\n1. Testing basic connectivity...")
    for service_name, base_url in BASE_URLS.items():
        test_endpoint(service_name, '/', 'GET')
    
    # Test auth service to get token
    print("\n2. Testing auth service...")
    auth_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    auth_response = test_endpoint('auth_service', '/token', 'POST', data=auth_data)
    
    jwt_token = None
    if auth_response and auth_response.status_code == 200:
        try:
            token_data = auth_response.json()
            jwt_token = token_data.get('access_token')
            print(f"✅ Got JWT token: {jwt_token[:50]}..." if jwt_token else "❌ No token in response")
        except:
            print("❌ Could not parse auth response")
    
    # Test history endpoints
    print("\n3. Testing history endpoints...")
    
    if jwt_token:
        auth_headers = {"Authorization": f"Bearer {jwt_token}"}
        
        # Test URL Summarizer History
        test_endpoint('url_summarizer', '/history', 'GET', auth_headers)
        
        # Test File Service History  
        test_endpoint('file_service', '/api/files/history/', 'GET', auth_headers)
        
        # Test Summarization Backend History
        test_endpoint('summarization_backend', '/api/summaries/history/', 'GET', auth_headers)
        
        # Test Comparison Service History (no auth needed, uses user_id param)
        # First create a comparison
        comparison_data = {
            "source1_content": "This is the first document about technology and innovation.",
            "source2_content": "This is the second document about science and discovery.",
            "user_id": "1"
        }
        test_endpoint('comparison_service', '/api/compare', 'POST', data=comparison_data)
        
        # Then test history
        test_endpoint('comparison_service', '/api/history/?user_id=1', 'GET')
        
    else:
        print("❌ No JWT token available, testing without auth...")
        
        # Test endpoints without auth
        test_endpoint('url_summarizer', '/history', 'GET')
        test_endpoint('file_service', '/api/files/history/', 'GET')
        test_endpoint('summarization_backend', '/api/summaries/history/', 'GET')
        
        # Test comparison service - create then get history
        comparison_data = {
            "source1_content": "This is the first document about technology.",
            "source2_content": "This is the second document about science.",
            "user_id": "1"
        }
        test_endpoint('comparison_service', '/api/compare', 'POST', data=comparison_data)
        test_endpoint('comparison_service', '/api/history/?user_id=1', 'GET')
    
    print("\n🏁 Testing complete!")

if __name__ == "__main__":
    main()
