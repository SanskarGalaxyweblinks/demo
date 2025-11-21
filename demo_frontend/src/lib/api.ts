// lib/api.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

// Types for API requests and responses
export interface AuthRequest {
  email: string;
  password: string;
}

export interface RegisterRequest extends AuthRequest {
  full_name: string;
}

export interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
    full_name: string;
    created_at: string;
  };
}

export interface EmailClassificationRequest {
  subject: string;
  body: string;
}

export interface EmailClassificationResponse {
  category: "Onboarding" | "Dispute" | "Other";
  priority: "High" | "Medium" | "Low";
  sentiment: "Positive" | "Negative" | "Neutral";
  confidence: number;
  tags: string[];
}

export interface DocumentAnalysisResponse {
  documentType: string;
  pageCount: number;
  entities: string[];
  detectedCurrency?: string;
  confidence: number;
  receivedAt: string;
  preview?: string;
  extractedData?: any;
  processingTime: number;
}

export interface TamperDetectionResponse {
  isAuthentic: boolean;
  confidenceScore: number;
  detectedIssues: string[];
  riskLevel: "Low" | "Medium" | "High";
  analysisDetails: {
    metadataConsistency: boolean;
    pixelAnalysis: boolean;
    compressionArtifacts: boolean;
    editingTraces: boolean;
  };
  processingTime: number;
}

export interface CustomerRecord {
  id: string;
  name: string;
  email: string;
  status: "onboarded" | "pending" | "rejected";
  documentType: string;
  submissionDate: string;
  verificationStatus: "verified" | "pending" | "flagged";
  createdBy?: string;
  createdAt?: string;
}

export interface CreateCustomerRequest {
  name: string;
  email: string;
  status?: string;
  document_type: string;
  verification_status?: string;
}

// NEW: KYC Data Management Types
export interface KYCRecord {
  id: number;
  customer_name: string;
  customer_email: string;
  odoo_customer_id?: number;
  email_classification?: {
    category: string;
    priority: string;
    sentiment: string;
    confidence: number;
    tags: string[];
    reasoning: string;
  };
  document_analysis?: {
    document_type: string;
    confidence: number;
    entities: string[];
    extracted_data?: any;
  };
  tamper_detection?: {
    is_authentic: boolean;
    risk_level: string;
    confidence_score: number;
    detected_issues: string[];
  };
  confidence_score: number;
  processing_timestamp: string;
  processed_by: string;
  created_date: string;
  status: string;
}

export interface UserKYCStats {
  total_records: number;
  confidence_breakdown: {
    high: number;
    medium: number;
    low: number;
  };
  category_breakdown: {
    onboarding: number;
    dispute: number;
    other: number;
  };
  last_processing?: string;
}

export interface KYCDataResponse {
  records: KYCRecord[];
  total_count: number;
  user_stats: UserKYCStats;
}

export interface KYCDeleteResponse {
  success: boolean;
  message: string;
  deleted_record_id?: number;
}

export interface KYCDashboardData {
  user_email: string;
  overview_stats: UserKYCStats;
  recent_records: Array<{
    id: number;
    customer_name: string;
    email_category: string;
    confidence_score: number;
    processing_date: string;
    status: string;
    document_types: string[];
  }>;
  processing_trends: {
    daily_volume: number;
    weekly_growth: string;
    accuracy_trend: string;
    avg_processing_time: string;
  };
  system_health: {
    odoo_connection: string;
    ai_services: string;
    processing_queue: string;
    last_backup: string;
  };
}

// ERP Sync Types
export interface ErpSyncRequest {
  customerName: string;
  orderAmount: number;
  currency: string;
}

export interface ErpSyncResponse {
  recordId: string;
  status: string;
  synced: boolean;
  timestamp: string;
  odooCustomerId?: number;
  odooLeadId?: number;
  payload?: {
    customerName: string;
    orderAmount: number;
    currency: string;
  };
  error?: string;
}

// Complete KYC workflow request/response types
export interface KYCWorkflowRequest {
  subject: string;
  body: string;
  attachments?: File[];
}

export interface KYCWorkflowResponse {
  emailClassification: EmailClassificationResponse;
  documentAnalysis?: DocumentAnalysisResponse;
  tamperDetection?: TamperDetectionResponse;
  erpIntegration: {
    customerId: string;
    status: string;
    message: string;
  };
  processingTime: number;
}

// Utility function for making authenticated requests
async function fetchWithAuth(url: string, options: RequestInit = {}, token?: string): Promise<any> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

// Authentication API
export const authAPI = {
  async login(credentials: AuthRequest): Promise<AuthResponse> {
    return fetchWithAuth("/auth/login", {
      method: "POST",
      body: JSON.stringify(credentials),
    });
  },

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    return fetchWithAuth("/auth/register", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  },

  async googleLogin(data: { email: string; full_name: string }): Promise<AuthResponse> {
    return fetchWithAuth("/auth/google", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async getSession(token: string): Promise<AuthResponse["user"]> {
    return fetchWithAuth("/auth/session", {
      method: "GET",
    }, token);
  },

  async logout(): Promise<void> {
    return fetchWithAuth("/auth/logout", {
      method: "POST",
    });
  },
};

// Email Classification API
export const emailAPI = {
  async classify(data: EmailClassificationRequest, token?: string): Promise<EmailClassificationResponse> {
    return fetchWithAuth("/emails/classify", {
      method: "POST",
      body: JSON.stringify(data),
    }, token);
  },
};

// Document Processing API
export const documentAPI = {
  async analyze(file: File, token?: string): Promise<DocumentAnalysisResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/documents/analyze`, {
      method: "POST",
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  },

  async detectTamper(file: File, token?: string): Promise<TamperDetectionResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/documents/tamper-detect`, {
      method: "POST",
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  },
};

// ERP/Customer Management API
export const erpAPI = {
  // Odoo ERP Sync
  async syncToErp(data: ErpSyncRequest, token?: string): Promise<ErpSyncResponse> {
    return fetchWithAuth("/erp/sync", {
      method: "POST",
      body: JSON.stringify(data),
    }, token);
  },

  async getCustomers(token?: string): Promise<{ customers: any[], total: number }> {
    return fetchWithAuth("/erp/customers", {
      method: "GET",
    }, token);
  },

  async createCustomer(data: CreateCustomerRequest, token?: string): Promise<CustomerRecord> {
    return fetchWithAuth("/erp/customers", {
      method: "POST",
      body: JSON.stringify(data),
    }, token);
  },

  async getCustomer(customerId: string, token?: string): Promise<CustomerRecord> {
    return fetchWithAuth(`/erp/customers/${customerId}`, {
      method: "GET",
    }, token);
  },

  async deleteCustomer(customerId: string, token?: string): Promise<void> {
    return fetchWithAuth(`/erp/customers/${customerId}`, {
      method: "DELETE",
    }, token);
  },

  async getStats(token?: string): Promise<{
    total_customers: number;
    recent_customers?: number;
    user_kyc_records?: number;
    odoo_connection?: string;
    last_sync?: string;
    error?: string;
  }> {
    return fetchWithAuth("/erp/stats", {
      method: "GET",
    }, token);
  },

  // ERP Health Check
  async healthCheck(): Promise<{
    status: string;
    odoo_connection: string;
    database?: string;
    kyc_data_management?: string;
    message: string;
    error?: string;
  }> {
    return fetchWithAuth("/erp/health", {
      method: "GET",
    });
  },

  // KYC Record Creation in Odoo (Legacy)
  async createKycRecord(data: {
    customer_name: string;
    customer_email: string;
    document_types: string[];
    extraction_data: any;
  }, token?: string): Promise<any> {
    return fetchWithAuth("/erp/kyc", {
      method: "POST",
      body: JSON.stringify(data),
    }, token);
  },

  // =================== NEW KYC DATA MANAGEMENT API ===================

  // Get user's KYC processing records
  async getKYCRecords(options: {
    limit?: number;
    offset?: number;
  } = {}, token?: string): Promise<KYCDataResponse> {
    const params = new URLSearchParams();
    if (options.limit) params.append('limit', options.limit.toString());
    if (options.offset) params.append('offset', options.offset.toString());

    const url = `/erp/kyc/records${params.toString() ? `?${params.toString()}` : ''}`;
    return fetchWithAuth(url, { method: "GET" }, token);
  },

  // Delete a specific KYC record
  async deleteKYCRecord(recordId: number, token?: string): Promise<KYCDeleteResponse> {
    return fetchWithAuth(`/erp/kyc/records/${recordId}`, {
      method: "DELETE",
    }, token);
  },

  // Get user's KYC processing statistics
  async getKYCStats(token?: string): Promise<UserKYCStats> {
    return fetchWithAuth("/erp/kyc/stats", {
      method: "GET",
    }, token);
  },

  // Get complete KYC dashboard data
  async getKYCDashboard(token?: string): Promise<KYCDashboardData> {
    return fetchWithAuth("/erp/kyc/dashboard", {
      method: "GET",
    }, token);
  },

  // Bulk delete multiple KYC records
  async bulkDeleteKYCRecords(recordIds: number[], token?: string): Promise<{
    success: boolean;
    deleted_records: number[];
    failed_records: number[];
    message: string;
  }> {
    return fetchWithAuth("/erp/kyc/bulk-delete", {
      method: "POST",
      body: JSON.stringify({ record_ids: recordIds }),
    }, token);
  },
};

// Complete KYC Workflow API (for the new integrated workflow)
export const kycWorkflowAPI = {
  async processComplete(data: KYCWorkflowRequest, token?: string): Promise<KYCWorkflowResponse> {
    const formData = new FormData();
    formData.append("subject", data.subject);
    formData.append("body", data.body);
    
    // Add attachments if any
    if (data.attachments) {
      data.attachments.forEach((file, index) => {
        formData.append(`attachment_${index}`, file);
      });
    }

    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}/kyc/process-complete`, {
      method: "POST",
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  },

  async processEmail(data: EmailClassificationRequest, token?: string): Promise<EmailClassificationResponse> {
    return emailAPI.classify(data, token);
  },

  async processDocuments(files: File[], token?: string): Promise<DocumentAnalysisResponse[]> {
    const results = await Promise.all(
      files.map(file => documentAPI.analyze(file, token))
    );
    return results;
  },

  async detectTamperBatch(files: File[], token?: string): Promise<TamperDetectionResponse[]> {
    const results = await Promise.all(
      files.map(file => documentAPI.detectTamper(file, token))
    );
    return results;
  },

  async createCustomerRecord(data: {
    name: string;
    email: string;
    emailClassification: EmailClassificationResponse;
    documentAnalysis?: DocumentAnalysisResponse[];
    tamperDetection?: TamperDetectionResponse[];
  }, token?: string): Promise<CustomerRecord> {
    const customerData: CreateCustomerRequest = {
      name: data.name,
      email: data.email,
      status: data.emailClassification.category === "Onboarding" ? "pending" : "other",
      document_type: data.documentAnalysis ? 
        data.documentAnalysis.map(doc => doc.documentType).join(", ") : 
        "Email Only",
      verification_status: data.tamperDetection?.some(t => !t.isAuthentic) ? "flagged" : "pending"
    };

    return erpAPI.createCustomer(customerData, token);
  },
};

// =================== NEW KYC DATA MANAGEMENT UTILITIES ===================

// Convenience functions for KYC data management
export const kycDataAPI = {
  // Get user's KYC records with pagination
  async getUserRecords(page: number = 1, pageSize: number = 10, token?: string): Promise<KYCDataResponse> {
    const offset = (page - 1) * pageSize;
    return erpAPI.getKYCRecords({ limit: pageSize, offset }, token);
  },

  // Get recent KYC records (last 10)
  async getRecentRecords(token?: string): Promise<KYCRecord[]> {
    const response = await erpAPI.getKYCRecords({ limit: 10, offset: 0 }, token);
    return response.records;
  },

  // Search KYC records by customer name (client-side filtering)
  async searchRecords(searchTerm: string, token?: string): Promise<KYCRecord[]> {
    const response = await erpAPI.getKYCRecords({ limit: 100 }, token);
    return response.records.filter(record => 
      record.customer_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      record.customer_email.toLowerCase().includes(searchTerm.toLowerCase())
    );
  },

  // Get records by status
  async getRecordsByStatus(status: string, token?: string): Promise<KYCRecord[]> {
    const response = await erpAPI.getKYCRecords({ limit: 100 }, token);
    return response.records.filter(record => record.status.toLowerCase() === status.toLowerCase());
  },

  // Get high confidence records (confidence > 80%)
  async getHighConfidenceRecords(token?: string): Promise<KYCRecord[]> {
    const response = await erpAPI.getKYCRecords({ limit: 100 }, token);
    return response.records.filter(record => record.confidence_score > 0.8);
  },

  // Delete multiple records with confirmation
  async deleteRecordsWithConfirmation(recordIds: number[], token?: string): Promise<{
    success: boolean;
    message: string;
    details: any;
  }> {
    try {
      const result = await erpAPI.bulkDeleteKYCRecords(recordIds, token);
      return {
        success: result.success,
        message: result.message,
        details: result
      };
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Delete operation failed',
        details: { error }
      };
    }
  },

  // Export KYC data to CSV format (client-side)
  exportToCSV(records: KYCRecord[]): string {
    const headers = [
      'ID', 'Customer Name', 'Email', 'Status', 'Category', 'Confidence Score',
      'Processing Date', 'Document Type', 'Risk Level', 'Processed By'
    ];

    const csvData = records.map(record => [
      record.id,
      record.customer_name,
      record.customer_email,
      record.status,
      record.email_classification?.category || 'N/A',
      record.confidence_score,
      record.processing_timestamp,
      record.document_analysis?.document_type || 'N/A',
      record.tamper_detection?.risk_level || 'N/A',
      record.processed_by
    ]);

    const csvContent = [headers, ...csvData]
      .map(row => row.map(field => `"${field}"`).join(','))
      .join('\n');

    return csvContent;
  },

  // Download CSV file
  downloadCSV(records: KYCRecord[], filename: string = 'kyc-records.csv'): void {
    const csvContent = this.exportToCSV(records);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', filename);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }
};

// Health check
export const healthAPI = {
  async check(): Promise<{ message: string }> {
    return fetchWithAuth("/health");
  },
};

// Error handling utilities
export class APIError extends Error {
  constructor(
    message: string,
    public status?: number,
    public details?: any
  ) {
    super(message);
    this.name = "APIError";
  }
}

// Export all APIs
export default {
  auth: authAPI,
  email: emailAPI,
  document: documentAPI,
  erp: erpAPI,
  kycWorkflow: kycWorkflowAPI,
  kycData: kycDataAPI,
  health: healthAPI,
};