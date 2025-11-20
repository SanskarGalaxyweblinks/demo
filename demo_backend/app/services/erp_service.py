from __future__ import annotations

import requests
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

class OdooClient:
    def __init__(self):
        self.url = "http://3.6.198.245:8089"
        self.username = "shoaib.khan@galaxyweblinks.com"
        self.password = "Admin@123"
        self.db = None  # Will be set after authentication
        self.uid = None
        self.session_id = None
        
    def authenticate(self) -> bool:
        """Authenticate with Odoo and get database name"""
        try:
            # First get database list
            response = requests.post(f"{self.url}/web/database/list", json={})
            if response.status_code == 200:
                result = response.json()
                if result.get('result') and len(result['result']) > 0:
                    self.db = result['result'][0]  # Use first available database
                else:
                    print("No databases found")
                    return False
            
            # Now authenticate with the database
            auth_response = requests.post(f"{self.url}/web/session/authenticate", json={
                'params': {
                    'db': self.db,
                    'login': self.username,
                    'password': self.password
                }
            })
            
            if auth_response.status_code == 200:
                result = auth_response.json()
                if result.get('result') and result['result'].get('uid'):
                    self.uid = result['result']['uid']
                    self.session_id = auth_response.cookies.get('session_id')
                    return True
            return False
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def create_record(self, model: str, data: Dict[str, Any]) -> Optional[int]:
        """Create record in Odoo"""
        if not self.uid:
            if not self.authenticate():
                return None
                
        try:
            response = requests.post(f"{self.url}/web/dataset/call_kw", 
                json={
                    'params': {
                        'model': model,
                        'method': 'create',
                        'args': [data],
                        'kwargs': {}
                    }
                },
                cookies={'session_id': self.session_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result'):
                    return result['result']
            return None
        except Exception as e:
            print(f"Create record failed: {e}")
            return None
    
    def search_records(self, model: str, domain: List = None, fields: List = None) -> List[Dict]:
        """Search records in Odoo"""
        if not self.uid:
            if not self.authenticate():
                return []
                
        try:
            response = requests.post(f"{self.url}/web/dataset/call_kw",
                json={
                    'params': {
                        'model': model,
                        'method': 'search_read',
                        'args': [domain or []],
                        'kwargs': {'fields': fields or []}
                    }
                },
                cookies={'session_id': self.session_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result'):
                    return result['result']
            return []
        except Exception as e:
            print(f"Search records failed: {e}")
            return []

# Global Odoo client instance
_odoo_client = OdooClient()

def create_customer_in_odoo(name: str, email: str = None) -> Optional[int]:
    """Create customer in Odoo CRM"""
    data = {
        'name': name,
        'is_company': False,
        'customer_rank': 1
    }
    if email:
        data['email'] = email
        
    return _odoo_client.create_record('res.partner', data)

def create_support_ticket_in_odoo(customer_name: str, subject: str, description: str) -> Optional[int]:
    """Create support ticket in Odoo Helpdesk"""
    # First create customer
    customer_id = create_customer_in_odoo(customer_name)
    if not customer_id:
        return None
        
    data = {
        'name': subject,
        'description': description,
        'partner_id': customer_id
    }
    # Try helpdesk.ticket first, fallback to project.task
    ticket_id = _odoo_client.create_record('helpdesk.ticket', data)
    if not ticket_id:
        # Fallback to project task if helpdesk module not installed
        ticket_id = _odoo_client.create_record('project.task', data)
    return ticket_id

def create_sales_lead_in_odoo(customer_name: str, opportunity_name: str, amount: float = 0) -> Optional[int]:
    """Create sales lead in Odoo CRM"""
    customer_id = create_customer_in_odoo(customer_name)
    if not customer_id:
        return None
        
    data = {
        'name': opportunity_name,
        'partner_id': customer_id,
        'expected_revenue': amount
    }
    return _odoo_client.create_record('crm.lead', data)

async def get_customer_records(db: AsyncSession) -> List[Dict[str, Any]]:
    """Get customer records from Odoo"""
    records = _odoo_client.search_records('res.partner', 
        domain=[('customer_rank', '>', 0)], 
        fields=['name', 'email', 'create_date']
    )
    return records

async def create_customer_record(
    db: AsyncSession, 
    customer_data: Dict[str, Any],
    created_by_user: Any
) -> Dict[str, Any]:
    """Create customer record in Odoo"""
    customer_id = create_customer_in_odoo(
        customer_data.get("name", "Unknown Customer"),
        customer_data.get("email")
    )
    
    if customer_id:
        return {
            "id": customer_id,
            "name": customer_data.get("name", "Unknown Customer"),
            "email": customer_data.get("email"),
            "status": "created",
            "odoo_id": customer_id,
            "created_at": datetime.utcnow().isoformat()
        }
    return {}

def create_kyc_record(
    customer_name: str,
    customer_email: str, 
    document_types: List[str],
    extraction_data: Dict[str, Any],
    user: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Create KYC customer record in Odoo"""
    # Create customer in Odoo
    customer_id = create_customer_in_odoo(customer_name, customer_email)
    
    # Create support ticket for KYC verification
    subject = f"KYC Verification - {customer_name}"
    description = f"Documents: {', '.join(document_types)}\nConfidence: {extraction_data.get('confidence', 0.0)}"
    
    ticket_id = create_support_ticket_in_odoo(customer_name, subject, description)
    
    return {
        "customer_id": customer_id,
        "ticket_id": ticket_id,
        "name": customer_name,
        "email": customer_email,
        "status": "pending" if extraction_data.get("confidence", 0) < 0.9 else "verified",
        "document_types": ", ".join(document_types),
        "confidence_score": extraction_data.get("confidence", 0.0),
        "processing_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "processed_by": user.get("email") if user else "system"
    }

def sync_to_erp(
    customer_name: str,
    order_amount: float,
    currency: str,
    user: dict[str, Any] | None,
):
    """Create customer and sales opportunity in Odoo"""
    try:
        # Create customer
        customer_id = create_customer_in_odoo(customer_name)
        
        # Create sales opportunity
        opportunity_name = f"Order - {customer_name}"
        lead_id = create_sales_lead_in_odoo(customer_name, opportunity_name, order_amount)
        
        record_id = f"ODOO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "record_id": record_id,
            "status": "Success" if customer_id and lead_id else "Partial Success",
            "synced": True,
            "timestamp": datetime.utcnow(),
            "odoo_customer_id": customer_id,
            "odoo_lead_id": lead_id,
            "payload": {
                "customerName": customer_name,
                "orderAmount": order_amount,
                "currency": currency
            }
        }
    except Exception as e:
        return {
            "record_id": f"ERROR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "status": "Error",
            "synced": False,
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }