from __future__ import annotations

import requests
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import json

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
    
    def update_record(self, model: str, record_id: int, data: Dict[str, Any]) -> bool:
        """Update record in Odoo"""
        if not self.uid:
            if not self.authenticate():
                return False
                
        try:
            response = requests.post(f"{self.url}/web/dataset/call_kw",
                json={
                    'params': {
                        'model': model,
                        'method': 'write',
                        'args': [[record_id], data],
                        'kwargs': {}
                    }
                },
                cookies={'session_id': self.session_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('result', False)
            return False
        except Exception as e:
            print(f"Update record failed: {e}")
            return False
    
    def delete_record(self, model: str, record_id: int) -> bool:
        """Delete record in Odoo"""
        if not self.uid:
            if not self.authenticate():
                return False
                
        try:
            response = requests.post(f"{self.url}/web/dataset/call_kw",
                json={
                    'params': {
                        'model': model,
                        'method': 'unlink',
                        'args': [[record_id]],
                        'kwargs': {}
                    }
                },
                cookies={'session_id': self.session_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('result', False)
            return False
        except Exception as e:
            print(f"Delete record failed: {e}")
            return False

# Global Odoo client instance
_odoo_client = OdooClient()

# =================== BASIC CUSTOMER CREATION ===================

def create_customer_in_odoo(name: str, email: str = None) -> Optional[int]:
    """Create customer in Odoo CRM - using only basic fields"""
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

# =================== KYC DATA MANAGEMENT USING FREE MODELS ===================

def create_kyc_processing_record(
    customer_id: int,
    user_email: str,
    email_data: Dict[str, Any],
    document_data: Optional[Dict[str, Any]] = None,
    tamper_data: Optional[Dict[str, Any]] = None
) -> Optional[int]:
    """Create KYC processing record using crm.lead model (FREE)"""
    
    # Prepare processing summary
    processing_summary = {
        "email_classification": email_data,
        "document_analysis": document_data,
        "tamper_detection": tamper_data,
        "processing_timestamp": datetime.utcnow().isoformat(),
        "processed_by": user_email
    }
    
    # Create lead record to store KYC data
    lead_data = {
        'name': f"KYC Processing - {email_data.get('customer_name', 'Unknown')}",
        'partner_id': customer_id,
        'type': 'opportunity',  # Use as KYC tracking
        'description': json.dumps(processing_summary, indent=2),  # Store all AI results
        'expected_revenue': 0,  # Not used for KYC
        'stage_id': 1,  # Default stage
        # Custom fields using available fields
        'email_from': user_email,
        'phone': email_data.get('confidence', 0) * 100,  # Store confidence as "phone" number
    }
    
    print(f"[KYC] Creating KYC processing record for customer {customer_id}")
    result = _odoo_client.create_record('crm.lead', lead_data)
    print(f"[KYC] KYC record creation result: {result}")
    return result

def get_user_kyc_records(user_email: str) -> List[Dict[str, Any]]:
    """Get all KYC processing records for a user"""
    try:
        # Search for leads created by this user (KYC records)
        domain = [
            ('email_from', '=', user_email),
            ('name', 'like', 'KYC Processing')
        ]
        
        fields = [
            'id', 'name', 'partner_id', 'description', 'create_date', 
            'phone', 'email_from', 'stage_id'
        ]
        
        records = _odoo_client.search_records('crm.lead', domain=domain, fields=fields)
        
        processed_records = []
        for record in records:
            try:
                # Parse the stored AI processing data
                processing_data = json.loads(record.get('description', '{}'))
                
                processed_record = {
                    'id': record['id'],
                    'customer_name': processing_data.get('email_classification', {}).get('customer_name', 'Unknown'),
                    'email_classification': processing_data.get('email_classification'),
                    'document_analysis': processing_data.get('document_analysis'),
                    'tamper_detection': processing_data.get('tamper_detection'),
                    'processing_timestamp': processing_data.get('processing_timestamp'),
                    'processed_by': processing_data.get('processed_by'),
                    'confidence_score': record.get('phone', 0) / 100 if record.get('phone') else 0,
                    'odoo_customer_id': record.get('partner_id', [None])[0] if record.get('partner_id') else None,
                    'created_date': record.get('create_date'),
                }
                processed_records.append(processed_record)
                
            except json.JSONDecodeError:
                # Handle records with invalid JSON
                processed_record = {
                    'id': record['id'],
                    'customer_name': 'Data Error',
                    'error': 'Invalid processing data format'
                }
                processed_records.append(processed_record)
        
        return processed_records
        
    except Exception as e:
        print(f"[KYC] Error fetching user records: {e}")
        return []

def delete_user_kyc_record(record_id: int, user_email: str) -> bool:
    """Delete a KYC record (only if it belongs to the user)"""
    try:
        # First verify the record belongs to this user
        domain = [
            ('id', '=', record_id),
            ('email_from', '=', user_email),
            ('name', 'like', 'KYC Processing')
        ]
        
        records = _odoo_client.search_records('crm.lead', domain=domain, fields=['id'])
        
        if not records:
            print(f"[KYC] Record {record_id} not found or doesn't belong to user {user_email}")
            return False
        
        # Delete the record
        success = _odoo_client.delete_record('crm.lead', record_id)
        
        if success:
            print(f"[KYC] ✅ Deleted KYC record {record_id} for user {user_email}")
        else:
            print(f"[KYC] ❌ Failed to delete KYC record {record_id}")
            
        return success
        
    except Exception as e:
        print(f"[KYC] Error deleting record {record_id}: {e}")
        return False

def get_user_kyc_stats(user_email: str) -> Dict[str, Any]:
    """Get KYC processing statistics for a user"""
    try:
        records = get_user_kyc_records(user_email)
        
        total_records = len(records)
        high_confidence = sum(1 for r in records if r.get('confidence_score', 0) > 0.8)
        medium_confidence = sum(1 for r in records if 0.5 <= r.get('confidence_score', 0) <= 0.8)
        low_confidence = sum(1 for r in records if r.get('confidence_score', 0) < 0.5)
        
        # Count by categories
        onboarding_count = sum(1 for r in records if r.get('email_classification', {}).get('category') == 'Onboarding')
        dispute_count = sum(1 for r in records if r.get('email_classification', {}).get('category') == 'Dispute')
        other_count = sum(1 for r in records if r.get('email_classification', {}).get('category') == 'Other')
        
        return {
            'total_records': total_records,
            'confidence_breakdown': {
                'high': high_confidence,
                'medium': medium_confidence,
                'low': low_confidence
            },
            'category_breakdown': {
                'onboarding': onboarding_count,
                'dispute': dispute_count,
                'other': other_count
            },
            'last_processing': records[0].get('processing_timestamp') if records else None
        }
        
    except Exception as e:
        print(f"[KYC] Error getting user stats: {e}")
        return {}

# =================== LEGACY FUNCTIONS (UPDATED TO USE NEW SYSTEM) ===================

def create_kyc_record(
    customer_name: str,
    customer_email: str, 
    document_types: List[str],
    extraction_data: Dict[str, Any],
    user: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Create KYC customer record using new custom data management system"""
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
    
    # Prepare email classification data
    email_data = {
        "customer_name": customer_name,
        "category": extraction_data.get("email_category", "Other"),
        "confidence": extraction_data.get("confidence", 0.8),
        "processing_method": extraction_data.get("processing_method", "AI Automation"),
        "document_types": document_types
    }
    
    # Create KYC processing record using our new system
    user_email = user.get("email") if user else "system@demo.com"
    processing_record_id = create_kyc_processing_record(
        customer_id=customer_id,
        user_email=user_email,
        email_data=email_data,
        document_data=extraction_data.get("document_analysis"),
        tamper_data=extraction_data.get("tamper_detection")
    )
    
    result = {
        "customer_id": customer_id,
        "ticket_id": processing_record_id,  # Using processing record as "ticket"
        "name": customer_name,
        "email": customer_email,
        "status": "pending" if extraction_data.get("confidence", 0) < 0.9 else "verified",
        "document_types": ", ".join(document_types) if document_types else "Email Only",
        "confidence_score": extraction_data.get("confidence", 0.0),
        "processing_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "processed_by": user_email
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
        
        # Create sales opportunity (standard CRM lead)
        opportunity_data = {
            'name': f"Sales Opportunity - {customer_name} ({currency} {order_amount})",
            'partner_id': customer_id,
            'expected_revenue': order_amount,
            'type': 'lead',  # Distinguish from KYC records
            'email_from': user.get("email") if user else "system@demo.com",
            'description': f"Sales opportunity created via ERP sync\nAmount: {currency} {order_amount}"
        }
        
        lead_id = _odoo_client.create_record('crm.lead', opportunity_data)
        
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

# =================== LEGACY HELPER FUNCTIONS ===================

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