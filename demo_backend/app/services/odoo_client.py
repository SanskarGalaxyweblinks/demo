import requests
import json
from typing import Optional, Dict, Any, List

class OdooClient:
    def __init__(self):
        self.url = "http://3.6.198.245:8089"
        self.username = "shoaib.khan@galaxyweblinks.com"
        self.password = "Admin@123"
        self.db = None
        self.uid = None
        self.session_id = None
        
    def get_database_list(self) -> List[str]:
        """Get list of available databases"""
        try:
            response = requests.post(f"{self.url}/web/database/list", json={})
            if response.status_code == 200:
                result = response.json()
                return result.get('result', [])
            return []
        except Exception as e:
            print(f"Failed to get database list: {e}")
            return []
    
    def authenticate(self) -> bool:
        """Login to Odoo and get user ID"""
        try:
            # Get database if not set
            if not self.db:
                db_list = self.get_database_list()
                if not db_list:
                    print("No databases found")
                    return False
                self.db = db_list[0]  # Use first available database
                
            response = requests.post(f"{self.url}/web/session/authenticate", json={
                'params': {
                    'db': self.db,
                    'login': self.username,
                    'password': self.password
                }
            })
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result') and result['result'].get('uid'):
                    self.uid = result['result']['uid']
                    self.session_id = response.cookies.get('session_id')
                    print(f"Successfully authenticated to database: {self.db}")
                    return True
            return False
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def create_record(self, model: str, data: Dict[str, Any]) -> Optional[int]:
        """Create a record in Odoo"""
        if not self.uid:
            if not self.authenticate():
                return None
                
        try:
            response = requests.post(f"{self.url}/web/dataset/call_kw", json={
                'params': {
                    'model': model,
                    'method': 'create',
                    'args': [data],
                    'kwargs': {}
                }
            }, cookies={'session_id': self.session_id})
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result'):
                    print(f"Created {model} record with ID: {result['result']}")
                    return result['result']
            return None
        except Exception as e:
            print(f"Create record failed for {model}: {e}")
            return None
    
    def search_records(self, model: str, domain: List = None, fields: List = None) -> List[Dict]:
        """Search records in Odoo"""
        if not self.uid:
            if not self.authenticate():
                return []
                
        try:
            response = requests.post(f"{self.url}/web/dataset/call_kw", json={
                'params': {
                    'model': model,
                    'method': 'search_read',
                    'args': [domain or []],
                    'kwargs': {'fields': fields or []}
                }
            }, cookies={'session_id': self.session_id})
            
            if response.status_code == 200:
                result = response.json()
                return result.get('result', [])
            return []
        except Exception as e:
            print(f"Search records failed for {model}: {e}")
            return []
    
    def create_customer(self, name: str, email: str = None) -> Optional[int]:
        """Create customer in CRM"""
        data = {
            'name': name,
            'is_company': False,
            'customer_rank': 1
        }
        if email:
            data['email'] = email
            
        return self.create_record('res.partner', data)
    
    def create_support_ticket(self, customer_name: str, subject: str, description: str) -> Optional[int]:
        """Create support ticket in Helpdesk or Project"""
        # First create customer if needed
        customer_id = self.create_customer(customer_name)
        if not customer_id:
            return None
            
        data = {
            'name': subject,
            'description': description,
            'partner_id': customer_id
        }
        
        # Try helpdesk.ticket first, then fallback to project.task
        ticket_id = self.create_record('helpdesk.ticket', data)
        if not ticket_id:
            ticket_id = self.create_record('project.task', data)
            
        return ticket_id
    
    def create_sales_lead(self, customer_name: str, opportunity_name: str, amount: float = 0) -> Optional[int]:
        """Create sales lead in CRM"""
        customer_id = self.create_customer(customer_name)
        if not customer_id:
            return None
            
        data = {
            'name': opportunity_name,
            'partner_id': customer_id,
            'expected_revenue': amount
        }
        return self.create_record('crm.lead', data)

# Global client instance
_odoo_client = None

def get_odoo_client() -> OdooClient:
    """Get configured Odoo client"""
    global _odoo_client
    if _odoo_client is None:
        _odoo_client = OdooClient()
    return _odoo_client