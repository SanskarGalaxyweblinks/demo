# demo_backend/app/services/erp_service.py
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
                print(f"[ODOO] Authentication failed for {model}")
                return None
                
        try:
            print(f"[ODOO] Creating {model} with data: {data}")
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
                    record_id = result['result']
                    print(f"[ODOO] ✅ Created {model} record ID: {record_id}")
                    return record_id
                elif result.get('error'):
                    print(f"[ODOO] ❌ API Error: {result['error']}")
                    return None
            return None
        except Exception as e:
            print(f"[ODOO] ❌ Exception creating {model}: {e}")
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

def find_customer_by_email(email: str) -> Optional[int]:
    """Find an existing customer in Odoo by email"""
    if not email:
        return None
    
    print(f"[ERP] Searching for customer with email: {email}")
    # Search for partner with this email
    # Note: 'ilike' is case-insensitive search in Odoo
    domain = [['email', '=', email]] 
    records = _odoo_client.search_records('res.partner', domain=domain, fields=['id', 'name'])
    
    if records and len(records) > 0:
        customer_id = records[0]['id']
        print(f"[ERP] ✅ Found existing customer: {records[0]['name']} (ID: {customer_id})")
        return customer_id
        
    print(f"[ERP] ⚠️ Customer not found for email: {email}")
    return None

def create_customer_in_odoo(name: str, email: str = None) -> Optional[int]:
    """Create customer in Odoo CRM - used during Signup"""
    data = {
        'name': name,
        'is_company': False
    }
    if email:
        data['email'] = email
        
    print(f"[ERP] Creating basic contact: {name} ({email})")
    result = _odoo_client.create_record('res.partner', data)
    print(f"[ERP] Contact creation result: {result}")
    return result

def create_helpdesk_ticket_in_odoo(customer_id: int, subject: str, description: str) -> Optional[int]:
    """Create helpdesk ticket in Odoo using proper field structure"""
    data = {
        'name': subject,
        'description': description,
        'partner_id': customer_id,
        'priority': '1'
    }
    print(f"[ERP] Creating helpdesk ticket: {subject}")
    result = _odoo_client.create_record('helpdesk.ticket', data)
    return result

def create_project_task_in_odoo(customer_id: int, task_name: str, description: str) -> Optional[int]:
    """Create project task in Odoo using proper field structure"""
    data = {
        'name': task_name,
        'partner_id': customer_id,
        'description': description,
    }
    print(f"[ERP] Creating project task: {task_name}")
    result = _odoo_client.create_record('project.task', data)
    return result

def create_support_ticket_in_odoo(customer_id: int, subject: str, description: str) -> Optional[int]:
    """
    Create support ticket in Odoo linked to an EXISTING customer ID.
    Tries helpdesk first, then project task.
    """
    if not customer_id:
        print("[ERP] ❌ Cannot create ticket: No customer ID provided")
        return None
    
    # Try helpdesk.ticket first
    ticket_id = create_helpdesk_ticket_in_odoo(customer_id, subject, description)
    
    if not ticket_id:
        print(f"[ERP] Helpdesk module not available, trying project.task")
        ticket_id = create_project_task_in_odoo(customer_id, subject, description)
        
    if not ticket_id:
        print(f"[ERP] ❌ Failed to create ticket or task in Odoo")
        return None
    
    print(f"[ERP] Support ticket/task creation result: {ticket_id}")
    return ticket_id

def create_sales_lead_in_odoo(customer_name: str, opportunity_name: str, amount: float = 0) -> Optional[int]:
    """Create sales lead in Odoo CRM (Legacy/ERP Demo)"""
    # NOTE: For the ERP Demo, we still might create a customer if one doesn't exist,
    # or we could refactor this to search as well. Keeping as is for now unless requested.
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
        domain=[], 
        fields=['name', 'email', 'create_date']
    )
    return records

async def create_customer_record(
    db: AsyncSession, 
    customer_data: Dict[str, Any],
    created_by_user: Any
) -> Dict[str, Any]:
    """Create customer record manually (ERP Demo)"""
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
    """
    Create KYC verification ticket in Odoo.
    UPDATED: Searches for existing customer instead of creating a new one.
    """
    print(f"[ERP] Starting KYC record creation for: {customer_name} ({customer_email})")
    
    # 1. FIND existing customer by email (from Signup)
    customer_id = find_customer_by_email(customer_email)
    
    if not customer_id:
        # Fallback: If not found by email (rare if signed up), try searching by name
        print(f"[ERP] Attempting fallback search by name: {customer_name}")
        domain = [['name', '=', customer_name]]
        records = _odoo_client.search_records('res.partner', domain=domain, fields=['id'])
        if records:
            customer_id = records[0]['id']
            print(f"[ERP] Found customer by name. ID: {customer_id}")
        else:
            print(f"[ERP] ❌ Customer not found in Odoo. Skipping ticket creation to avoid 'Unknown Customer' duplicates.")
            return {
                "customer_id": None,
                "ticket_id": None,
                "name": customer_name,
                "email": customer_email,
                "status": "skipped",
                "error": "Customer not found in Odoo (User must signup first)"
            }
    
    # 2. Create support ticket linked to the FOUND customer ID
    subject = f"KYC Verification Request - {customer_name}"
    description = f"""KYC Verification Request
    
Customer: {customer_name}
Email: {customer_email}
Document Types: {', '.join(document_types) if document_types else 'Email Only'}
AI Confidence Score: {extraction_data.get('confidence', 0.0):.2f}
Processing Method: {extraction_data.get('processing_method', 'AI Automation')}

This ticket was automatically created by the AI KYC processing system.
"""
    
    # Pass the ID, not the name
    ticket_id = create_support_ticket_in_odoo(customer_id, subject, description)
    
    result = {
        "customer_id": customer_id,
        "ticket_id": ticket_id,
        "name": customer_name,
        "email": customer_email,
        "status": "pending" if extraction_data.get("confidence", 0) < 0.9 else "verified",
        "document_types": ", ".join(document_types) if document_types else "Email Only",
        "confidence_score": extraction_data.get("confidence", 0.0),
        "processing_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "processed_by": user.get("email") if user else "system"
    }
    
    print(f"[ERP] KYC record creation completed: {result}")
    return result

def sync_to_erp(
    customer_name: str,
    order_amount: float,
    currency: str,
    user: dict[str, Any] | None,
):
    """Create customer and sales opportunity in Odoo (ERP Demo)"""
    try:
        print(f"[ERP] Starting ERP sync for: {customer_name}")
        
        # For ERP Demo, we still create customer as it's a standalone feature
        customer_id = create_customer_in_odoo(customer_name)
        
        opportunity_name = f"Sales Opportunity - {customer_name} ({currency} {order_amount})"
        lead_id = create_sales_lead_in_odoo(customer_name, opportunity_name, order_amount)
        
        record_id = f"ODOO-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        result = {
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
        return result
        
    except Exception as e:
        return {
            "record_id": f"ERROR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "status": "Error",
            "error": str(e)
        }