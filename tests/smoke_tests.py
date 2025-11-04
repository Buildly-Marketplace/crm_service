#!/usr/bin/env python3
"""
ForgeCRM Smoke Tests
Low-maintenance tests for basic functionality validation
"""

import os
import sys
import time
import requests
import json
from datetime import datetime, timedelta


class ForgeCRMSmokeTests:
    """Smoke tests for ForgeCRM service health and basic CRUD operations"""
    
    def __init__(self, base_url="http://localhost:8003", timeout=30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.auth_token = None
        self.test_data = {}
        
    def log(self, message):
        """Simple logging with timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
        
    def wait_for_service(self, max_attempts=10):
        """Wait for service to be ready"""
        self.log("Waiting for ForgeCRM service to be ready...")
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.base_url}/health_check/", timeout=5)
                if response.status_code == 200:
                    self.log("✅ Service is ready")
                    return True
            except requests.exceptions.RequestException:
                pass
                
            if attempt < max_attempts - 1:
                self.log(f"Service not ready, attempt {attempt + 1}/{max_attempts}, waiting...")
                time.sleep(3)
                
        self.log("❌ Service failed to become ready")
        return False
        
    def test_health_endpoint(self):
        """Test health endpoint returns 200 and expected structure"""
        self.log("Testing health endpoint...")
        
        try:
            response = requests.get(f"{self.base_url}/health_check/", timeout=self.timeout)
            
            # Check status code
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"
            
            # Check response content (HTML health check page)
            content = response.text.lower()
            
            # Check for health indicators in HTML
            assert 'working' in content or 'healthy' in content, "No health indicators found"
            assert 'database' in content, "Database check not found in health response"
            
            self.log("✅ Health endpoint test passed")
            return True
            
        except Exception as e:
            self.log(f"❌ Health endpoint test failed: {str(e)}")
            return False
            
    def get_auth_token(self):
        """Get authentication token for API calls"""
        self.log("Getting authentication token...")
        
        try:
            # Try to create a test user token
            # This assumes admin user exists (created by docker-entrypoint)
            login_data = {
                "username": "admin",
                "password": "admin"
            }
            
            response = requests.post(
                f"{self.base_url}/api-token-auth/",
                json=login_data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('token')
                if self.auth_token:
                    self.log("✅ Authentication token obtained")
                    return True
                    
            self.log(f"❌ Failed to get auth token: {response.status_code}")
            return False
            
        except Exception as e:
            self.log(f"❌ Auth token request failed: {str(e)}")
            return False
            
    def get_headers(self):
        """Get headers with auth token"""
        headers = {'Content-Type': 'application/json'}
        if self.auth_token:
            headers['Authorization'] = f'Token {self.auth_token}'
        return headers
        
    def test_accounts_crud(self):
        """Test basic CRUD operations on accounts endpoint"""
        self.log("Testing accounts CRUD operations...")
        
        try:
            headers = self.get_headers()
            
            # CREATE: Create a test account
            account_data = {
                "name": "Test Company Smoke",
                "account_type": "prospect",
                "industry": "technology", 
                "email": "test@smoketest.com",
                "phone": "555-TEST"
            }
            
            response = requests.post(
                f"{self.base_url}/accounts/",
                json=account_data,
                headers=headers,
                timeout=self.timeout
            )
            
            assert response.status_code in [200, 201], f"Create failed: {response.status_code}"
            created_account = response.json()
            account_uuid = created_account.get('account_uuid')
            assert account_uuid, "No account_uuid in response"
            
            self.test_data['account_uuid'] = account_uuid
            self.log("✅ Account created successfully")
            
            # READ: Get the account
            response = requests.get(
                f"{self.base_url}/accounts/{account_uuid}/",
                headers=headers,
                timeout=self.timeout
            )
            
            assert response.status_code == 200, f"Read failed: {response.status_code}"
            account = response.json()
            assert account['name'] == account_data['name'], "Account name mismatch"
            self.log("✅ Account read successfully")
            
            # UPDATE: Modify the account
            update_data = {"name": "Test Company Smoke Updated"}
            response = requests.patch(
                f"{self.base_url}/accounts/{account_uuid}/",
                json=update_data,
                headers=headers,
                timeout=self.timeout
            )
            
            assert response.status_code == 200, f"Update failed: {response.status_code}"
            updated_account = response.json()
            assert updated_account['name'] == update_data['name'], "Update not applied"
            self.log("✅ Account updated successfully")
            
            # LIST: Get accounts list
            response = requests.get(
                f"{self.base_url}/accounts/",
                headers=headers,
                timeout=self.timeout
            )
            
            assert response.status_code == 200, f"List failed: {response.status_code}"
            accounts_list = response.json()
            assert isinstance(accounts_list, (list, dict)), "Invalid list response format"
            self.log("✅ Accounts list retrieved successfully")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Accounts CRUD test failed: {str(e)}")
            return False
            
    def test_leads_basic(self):
        """Test basic leads functionality"""
        self.log("Testing leads basic operations...")
        
        try:
            headers = self.get_headers()
            
            # Create a test lead
            lead_data = {
                "full_name": "Smoke Test Lead",
                "company": "Smoke Test Co",
                "email": "lead@smoketest.com",
                "status": "new",
                "rating": "warm"
            }
            
            response = requests.post(
                f"{self.base_url}/leads/",
                json=lead_data,
                headers=headers,
                timeout=self.timeout
            )
            
            assert response.status_code in [200, 201], f"Lead create failed: {response.status_code}"
            lead = response.json()
            lead_uuid = lead.get('lead_uuid')
            assert lead_uuid, "No lead_uuid in response"
            
            self.test_data['lead_uuid'] = lead_uuid
            self.log("✅ Lead created successfully")
            
            # Test leads list
            response = requests.get(
                f"{self.base_url}/leads/",
                headers=headers,
                timeout=self.timeout
            )
            
            assert response.status_code == 200, f"Leads list failed: {response.status_code}"
            self.log("✅ Leads list retrieved successfully")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Leads test failed: {str(e)}")
            return False
            
    def test_opportunities_basic(self):
        """Test basic opportunities functionality"""
        self.log("Testing opportunities basic operations...")
        
        try:
            headers = self.get_headers()
            
            # Create opportunity (requires account)
            if 'account_uuid' not in self.test_data:
                self.log("⚠️  Skipping opportunities test - no account created")
                return True
                
            opportunity_data = {
                "name": "Smoke Test Opportunity",
                "account_uuid": self.test_data['account_uuid'],
                "stage": "prospecting",
                "amount": "10000.00",
                "probability": 50,
                "close_date": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            }
            
            response = requests.post(
                f"{self.base_url}/opportunities/",
                json=opportunity_data,
                headers=headers,
                timeout=self.timeout
            )
            
            assert response.status_code in [200, 201], f"Opportunity create failed: {response.status_code}"
            opportunity = response.json()
            opportunity_uuid = opportunity.get('opportunity_uuid')
            assert opportunity_uuid, "No opportunity_uuid in response"
            
            self.test_data['opportunity_uuid'] = opportunity_uuid
            self.log("✅ Opportunity created successfully")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Opportunities test failed: {str(e)}")
            return False
            
    def cleanup_test_data(self):
        """Clean up test data"""
        self.log("Cleaning up test data...")
        
        headers = self.get_headers()
        
        # Delete test records (ignore errors)
        cleanup_items = [
            ('opportunity_uuid', '/opportunities/'),
            ('lead_uuid', '/leads/'),
            ('account_uuid', '/accounts/')
        ]
        
        for uuid_key, endpoint in cleanup_items:
            if uuid_key in self.test_data:
                try:
                    uuid = self.test_data[uuid_key]
                    requests.delete(
                        f"{self.base_url}{endpoint}{uuid}/",
                        headers=headers,
                        timeout=5
                    )
                    self.log(f"✅ Cleaned up {uuid_key}")
                except Exception:
                    self.log(f"⚠️  Failed to cleanup {uuid_key}")
                    
    def run_all_tests(self):
        """Run all smoke tests"""
        self.log("=== ForgeCRM Smoke Tests Starting ===")
        
        # Wait for service
        if not self.wait_for_service():
            return False
            
        test_results = []
        
        # Health check (no auth required)
        test_results.append(self.test_health_endpoint())
        
        # Get auth token for API tests
        if self.get_auth_token():
            # API tests (require auth)
            test_results.append(self.test_accounts_crud())
            test_results.append(self.test_leads_basic())
            test_results.append(self.test_opportunities_basic())
            
            # Cleanup
            self.cleanup_test_data()
        else:
            self.log("⚠️  Skipping API tests - authentication failed")
            test_results.append(False)
            
        # Summary
        passed = sum(1 for result in test_results if result)
        total = len(test_results)
        
        self.log(f"=== Test Summary: {passed}/{total} tests passed ===")
        
        if passed == total:
            self.log("✅ All smoke tests PASSED")
            return True
        else:
            self.log("❌ Some smoke tests FAILED")
            return False


def main():
    """Main entry point"""
    # Get config from environment
    base_url = os.environ.get('FORGE_CRM_URL', 'http://localhost:8003')
    timeout = int(os.environ.get('TEST_TIMEOUT', '30'))
    
    # Run tests
    tester = ForgeCRMSmokeTests(base_url=base_url, timeout=timeout)
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()