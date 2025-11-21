from __future__ import annotations

import requests
from datetime import datetime
from typing import Any, Dict, List, Optional
import json

class OdooClient:
    def __init__(self):
        self.url = "http://3.6.198.245:8089"
        self.username = "shoaib.khan@galaxyweblinks.com"
        self.password = "Admin@123"
        self.db = None
        self.uid = None
        self.session_id = None
        
    def authenticate(self) -> bool:
        """Authenticate with Odoo and get database name"""
        try:
            if self.uid and self.session_id:
                return True

            # First get database list
            response = requests.post(f"{self.url}/web/database/list", json={})
            if response.status_code == 200:
                result = response.json()
                if result.get('result') and len(result['result']) > 0:
                    self.db = result['result'][0]
                else:
                    print("No databases found")
                    return False
            
            # Now authenticate
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
                else:
                    print(f"[ODOO] Error creating {model}: {result}")
            return None
        except Exception as e:
            print(f"[ODOO] Exception creating {model}: {e}")
            return None

    def create_attachment(self, name: str, datas: str, res_model: str, res_id: int) -> Optional[int]:
        """Create an attachment for a specific record"""
        attachment_data = {
            'name': name,
            'datas': datas,  # Base64 string
            'res_model': res_model,
            'res_id': res_id,
            'type': 'binary'
        }
        return self.create_record('ir.attachment', attachment_data)
    
    def search_records(self, model: str, domain: List = None, fields: List = None) -> List[Dict]:
        """Search records in Odoo"""
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
                return result.get('result', [])
            return []
        except Exception as e:
            print(f"Search records failed: {e}")
            return []
    
    def delete_record(self, model: str, record_id: int) -> bool:
        """Delete record in Odoo"""
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

def create_customer_in_odoo(name: str, email: str = None) -> Optional[int]:
    """Create customer in Odoo CRM (Contacts)"""
    # Check if customer already exists to avoid duplicates
    if email:
        existing = _odoo_client.search_records('res.partner', domain=[('email', '=', email)], fields=['id'])
        if existing:
            print(f"[ERP] Found existing customer: {name} ({email}) - ID: {existing[0]['id']}")
            return existing[0]['id']

    data = {
        'name': name,
        'is_company': False
    }
    if email:
        data['email'] = email
        
    print(f"[ERP] Creating contact: {name} ({email})")
    result = _odoo_client.create_record('res.partner', data)
    return result

def create_kyc_processing_record(
    customer_id: int,
    user_email: str,
    email_data: Dict[str, Any],
    email_body: str,
    document_data: Optional[Dict[str, Any]] = None,
    tamper_data: Optional[Dict[str, Any]] = None,
    attachments: List[Dict[str, str]] = None
) -> Optional[int]:
    """Create KYC processing record using crm.lead model"""
    
    subject = email_data.get('subject', 'No Subject')
    
    # Construct a detailed description for the CRM lead
    description = f"=== KYC Application Details ===\n"
    description += f"Subject: {subject}\n\n"
    description += f"--- Email Body ---\n{email_body}\n\n"
    
    description += f"--- AI Analysis Results ---\n"
    description += f"Category: {email_data.get('category')}\n"
    description += f"Confidence: {email_data.get('confidence')}\n"
    description += f"Sentiment: {email_data.get('sentiment')}\n"
    description += f"Priority: {email_data.get('priority')}\n"
    description += f"Tags: {', '.join(email_data.get('tags', []))}\n\n"
    
    if document_data:
        description += f"--- Document Analysis ---\n"
        description += json.dumps(document_data, indent=2) + "\n\n"
        
    if tamper_data:
        description += f"--- Tamper Detection ---\n"
        description += json.dumps(tamper_data, indent=2) + "\n"

    # Create lead record to store KYC data
    lead_data = {
        'name': f"KYC: {subject}",
        'partner_id': customer_id,
        'type': 'opportunity',
        'description': description,
        'expected_revenue': 0,
        'email_from': user_email,
        # We can store the full JSON in a hidden field or just rely on description
        # For dashboard compatibility, we still stash the JSON structure in a way we can parse back if needed,
        # but standard Odoo usage relies on the description field.
    }
    
    # Note: To keep Dashboard working, we might want to store the raw JSON somewhere.
    # However, sticking to standard Odoo fields is cleaner. 
    # We will append the raw JSON at the very end or use the description as the source of truth.
    # For the Dashboard.tsx to work without changes, it parses `description` as JSON.
    # To support BOTH Odoo UI readability AND the Dashboard, we will wrap the JSON in a special block 
    # or simply store the JSON string as the description (which is less readable in Odoo but keeps the app working).
    # Decision: Store the readable text, but also append a JSON block for the dashboard app to parse.
    
    full_json_data = {
        "email_classification": email_data,
        "document_analysis": document_data,
        "tamper_detection": tamper_data,
        "processing_timestamp": datetime.utcnow().isoformat(),
        "processed_by": user_email
    }
    
    # For the demo dashboard to continue working seamlessly, let's set the description to the JSON
    # but prepend a readable summary if possible. 
    # NOTE: The current dashboard parses the *entire* description as JSON. 
    # So we must store valid JSON. 
    lead_data['description'] = json.dumps(full_json_data, indent=2)
    
    print(f"[KYC] Creating CRM Lead for customer {customer_id}")
    lead_id = _odoo_client.create_record('crm.lead', lead_data)
    
    if lead_id and attachments:
        print(f"[KYC] Uploading {len(attachments)} attachments to Odoo CRM...")
        for att in attachments:
            _odoo_client.create_attachment(
                name=att['name'], 
                datas=att['content'], 
                res_model='crm.lead', 
                res_id=lead_id
            )
            
    return lead_id

def get_user_kyc_records(user_email: str) -> List[Dict[str, Any]]:
    """Get all KYC processing records for a user"""
    try:
        domain = [
            ('email_from', '=', user_email),
            ('name', 'like', 'KYC:')
        ]
        fields = ['id', 'name', 'partner_id', 'description', 'create_date', 'email_from']
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
                    'confidence_score': processing_data.get('email_classification', {}).get('confidence', 0),
                    'odoo_customer_id': record.get('partner_id', [None])[0] if record.get('partner_id') else None,
                    'created_date': record.get('create_date'),
                    'status': 'pending' # derive from data if needed
                }
                processed_records.append(processed_record)
            except json.JSONDecodeError:
                pass
        
        return processed_records
    except Exception as e:
        print(f"[KYC] Error fetching user records: {e}")
        return []

def delete_user_kyc_record(record_id: int, user_email: str) -> bool:
    """Delete a KYC record"""
    try:
        domain = [('id', '=', record_id), ('email_from', '=', user_email)]
        records = _odoo_client.search_records('crm.lead', domain=domain, fields=['id'])
        if not records:
            return False
        return _odoo_client.delete_record('crm.lead', record_id)
    except Exception:
        return False

def get_user_kyc_stats(user_email: str) -> Dict[str, Any]:
    """Get KYC processing statistics"""
    records = get_user_kyc_records(user_email)
    total = len(records)
    # Calculate simplified stats
    return {
        'total_records': total,
        'confidence_breakdown': {'high': 0, 'medium': 0, 'low': 0}, # Placeholder
        'category_breakdown': {'onboarding': 0, 'dispute': 0, 'other': 0},
        'last_processing': None
    }