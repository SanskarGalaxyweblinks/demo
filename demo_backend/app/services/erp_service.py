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
            
            print(f"[ODOO] Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"[ODOO] JSON result: {result}")
                
                if result.get('result'):
                    record_id = result['result']
                    print(f"[ODOO] ✅ Created {model} record ID: {record_id}")
                    return record_id
                elif result.get('error'):
                    print(f"[ODOO] ❌ API Error: {result['error']}")
                    return None
                else:
                    print(f"[ODOO] ❌ No result in response: {result}")
                    return None
            else:
                print(f"[ODOO] ❌ HTTP Error {response.status_code}: {response.text}")
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

def create_customer_in_odoo(name: str, email: str = None) -> Optional[int]:
    """Create customer in Odoo CRM - using only basic fields"""
    data = {
        'name': name,
        'is_company': False
        # Removed customer/customer_rank - just create basic contact
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
        'name': subject,  # Title/subject of the ticket
        'description': description,  # Detailed description
        'partner_id': customer_id,  # Customer who created the ticket
        'priority': '1'  # Priority level (0=Low, 1=Medium, 2=High, 3=Urgent)
        # Note: team_id, user_id, stage_id are optional and will use defaults
    }
    print(f"[ERP] Creating helpdesk ticket: {subject}")
    result = _odoo_client.create_record('helpdesk.ticket', data)
    print(f"[ERP] Helpdesk ticket creation result: {result}")
    return result

def create_project_task_in_odoo(customer_id: int, task_name: str, description: str) -> Optional[int]:
    """Create project task in Odoo using proper field structure"""
    data = {
        'name': task_name,  # Title/subject of the task
        'partner_id': customer_id,  # Customer linked to the task
        'description': description,  # Task description
        # Note: project_id, user_ids, stage_id are optional and will use defaults
        # If you have a specific project, you can add: 'project_id': project_id
    }
    print(f"[ERP] Creating project task: {task_name}")
    result = _odoo_client.create_record('project.task', data)
    print(f"[ERP] Project task creation result: {result}")
    return result

def create_support_ticket_in_odoo(customer_name: str, subject: str, description: str) -> Optional[int]:
    """Create support ticket in Odoo - tries helpdesk first, then project task"""
    # First create customer if we don't have ID
    customer_id = create_customer_in_odoo(customer_name)
    if not customer_id:
        print(f"[ERP] ❌ Failed to create customer for ticket: {customer_name}")
        return None
    
    # Try helpdesk.ticket first (if Helpdesk module is installed)
    ticket_id = create_helpdesk_ticket_in_odoo(customer_id, subject, description)
    
    if not ticket_id:
        print(f"[ERP] Helpdesk module not available, trying project.task")
        # Fallback to project task if helpdesk module not installed
        ticket_id = create_project_task_in_odoo(customer_id, subject, description)
        
    if not ticket_id:
        print(f"[ERP] ❌ Neither helpdesk nor project modules available")
        # Final fallback: just return customer_id since we created the customer successfully
        print(f"[ERP] ✅ Customer created successfully, skipping ticket creation")
        return customer_id
    
    print(f"[ERP] Support ticket/task creation result: {ticket_id}")
    return ticket_id

def create_sales_lead_in_odoo(customer_name: str, opportunity_name: str, amount: float = 0) -> Optional[int]:
    """Create sales lead in Odoo CRM"""
    customer_id = create_customer_in_odoo(customer_name)
    if not customer_id:
        print(f"[ERP] ❌ Failed to create customer for lead: {customer_name}")
        return None
        
    data = {
        'name': opportunity_name,
        'partner_id': customer_id,
        'expected_revenue': amount
    }
    print(f"[ERP] Creating sales lead: {opportunity_name}")
    result = _odoo_client.create_record('crm.lead', data)
    print(f"[ERP] Sales lead creation result: {result}")
    return result

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
    """Create KYC customer record in Odoo with proper ticket creation"""
    print(f"[ERP] Starting KYC record creation for: {customer_name}")
    
    # Create basic contact in Odoo
    customer_id = create_customer_in_odoo(customer_name, customer_email)
    if not customer_id:
        print(f"[ERP] ❌ Failed to create customer: {customer_name}")
        return {
            "customer_id": None,
            "ticket_id": None,
            "name": customer_name,
            "email": customer_email,
            "status": "failed",
            "error": "Customer creation failed"
        }
    
    # Create support ticket for KYC verification with proper fields
    subject = f"KYC Verification Request - {customer_name}"
    description = f"""KYC Verification Request
    
Customer: {customer_name}
Email: {customer_email}
Document Types: {', '.join(document_types) if document_types else 'Email Only'}
AI Confidence Score: {extraction_data.get('confidence', 0.0):.2f}
Processing Method: {extraction_data.get('processing_method', 'AI Automation')}

This ticket was automatically created by the AI KYC processing system.
Please review the customer information and complete the verification process.
"""
    
    ticket_id = create_support_ticket_in_odoo(customer_name, subject, description)
    
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
    """Create customer and sales opportunity in Odoo"""
    try:
        print(f"[ERP] Starting ERP sync for: {customer_name}")
        
        # Create customer
        customer_id = create_customer_in_odoo(customer_name)
        
        # Create sales opportunity
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
        
        print(f"[ERP] ERP sync completed: {result}")
        return result
        
    except Exception as e:
        error_result = {
            "record_id": f"ERROR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "status": "Error",
            "synced": False,
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }
        print(f"[ERP] ERP sync failed: {error_result}")
        return error_result