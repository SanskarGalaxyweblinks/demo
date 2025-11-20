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

// NEW: ERP Sync Types
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
async function fetchWithAuth(url: string, options: RequestInit = {}, token?: string) {
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
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
  // NEW: Odoo ERP Sync
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
    odoo_connection?: string;
    last_sync?: string;
    error?: string;
  }> {
    return fetchWithAuth("/erp/stats", {
      method: "GET",
    }, token);
  },

  // NEW: ERP Health Check
  async healthCheck(): Promise<{
    status: string;
    odoo_connection: string;
    database?: string;
    message: string;
    error?: string;
  }> {
    return fetchWithAuth("/erp/health", {
      method: "GET",
    });
  },

  // NEW: KYC Record Creation in Odoo
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
  health: healthAPI,
};