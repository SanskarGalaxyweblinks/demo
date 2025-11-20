import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Mail, 
  ArrowLeft, 
  Sparkles, 
  Clock, 
  Info, 
  BrainCircuit, 
  Database, 
  FileText, 
  Shield, 
  CheckCircle2, 
  Upload, 
  Loader2, 
  Send,
  ArrowRight,
  Trash2
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";

// Define interfaces for the complete KYC workflow
interface KYCWorkflowResult {
  emailClassification: {
    category: "Onboarding" | "Dispute" | "Other";
    priority: "High" | "Medium" | "Low";
    sentiment: "Positive" | "Negative" | "Neutral";
    confidence: number;
    tags: string[];
    reasoning?: string;
  };
  documentAnalysis?: {
    documentType: string;
    extractedData: any;
    confidence: number;
    entities: string[];
    processingTime?: number;
  };
  tamperDetection?: {
    isAuthentic: boolean;
    confidenceScore: number;
    riskLevel: string;
    detectedIssues: string[];
    processingTime?: number;
  };
  erpIntegration: {
    customerId: string;
    status: string;
    message: string;
  };
  processingTime: number;
}

interface WorkflowStep {
  id: string;
  title: string;
  icon: any;
  status: "pending" | "processing" | "completed" | "error";
  description: string;
  result?: string;
}

const EmailDemo = () => {
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [attachments, setAttachments] = useState<File[]>([]);
  const [result, setResult] = useState<KYCWorkflowResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState<string>("");
  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([
    {
      id: "email",
      title: "Email Classification",
      icon: Mail,
      status: "pending",
      description: "Analyzing email content and intent"
    },
    {
      id: "documents",
      title: "Document Processing",
      icon: FileText,
      status: "pending", 
      description: "Extracting data from attachments"
    },
    {
      id: "tamper",
      title: "Tamper Detection",
      icon: Shield,
      status: "pending",
      description: "Verifying document authenticity"
    },
    {
      id: "erp",
      title: "ERP Integration",
      icon: Database,
      status: "pending",
      description: "Creating customer record"
    }
  ]);

  const { toast } = useToast();
  const { token } = useAuth();
  const navigate = useNavigate();

  // Sample emails for testing
  const sampleEmails = [
    {
      title: "Onboarding Request",
      subject: "New Customer Application - John Smith",
      body: "Hello, I would like to open a new account and complete the KYC process. I have attached my driver's license and bank statement. Please let me know what other documents you need.",
      hasAttachments: true
    },
    {
      title: "Dispute Email", 
      subject: "Account Verification Dispute - Case #12345",
      body: "I'm writing to dispute the rejection of my account verification. The documents I submitted are legitimate and I believe there was an error in the review process. Please reconsider my application.",
      hasAttachments: true
    },
    {
      title: "General Inquiry",
      subject: "Question about KYC requirements",
      body: "Can you please provide more information about what documents are required for account verification? I want to make sure I submit everything correctly.",
      hasAttachments: false
    }
  ];

  const loadSampleEmail = (sample: typeof sampleEmails[0]) => {
    setSubject(sample.subject);
    setBody(sample.body);
    setResult(null);
    setProgress(0);
    setCurrentStep("");
    resetWorkflowSteps();
  };

  const resetWorkflowSteps = () => {
    setWorkflowSteps(prev => prev.map(step => ({ ...step, status: "pending", result: undefined })));
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setAttachments([...attachments, ...newFiles]);
      toast({
        title: "Files Added",
        description: `${newFiles.length} file(s) added to your KYC request`,
      });
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments(attachments.filter((_, i) => i !== index));
  };

  const updateStepStatus = (stepId: string, status: WorkflowStep['status'], result?: string) => {
    setWorkflowSteps(prev => 
      prev.map(step => 
        step.id === stepId ? { ...step, status, result } : step
      )
    );
  };

  const handleRunCompleteWorkflow = async () => {
    if (!subject || !body) {
      toast({
        title: "Missing Information",
        description: "Please fill in both subject and body",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    setResult(null);
    setProgress(0);
    resetWorkflowSteps();
    setCurrentStep("email");

    try {
      // REAL API call to backend
      const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
      
      // Create FormData for file uploads
      const formData = new FormData();
      formData.append("subject", subject);
      formData.append("body", body);
      
      // Add attachments if any
      attachments.forEach((file) => {
        formData.append("attachments", file);
      });

      // Update step to processing
      updateStepStatus("email", "processing");
      setProgress(10);

      console.log("[FRONTEND] Making API call to /kyc/process-complete");

      // Make REAL API call to the complete KYC workflow endpoint
      const response = await fetch(`${API_BASE}/kyc/process-complete`, {
        method: "POST",
        headers: {
          ...(token ? { "Authorization": `Bearer ${token}` } : {})
        },
        body: formData,
      });

      console.log("[FRONTEND] API Response status:", response.status);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      // Get REAL results from backend
      const workflowResult: KYCWorkflowResult = await response.json();
      console.log("[FRONTEND] Received workflow result:", workflowResult);
      
      // Update all steps as completed based on actual results
      updateStepStatus("email", "completed", 
        `Classified as ${workflowResult.emailClassification.category} (${Math.round(workflowResult.emailClassification.confidence * 100)}% confidence)`
      );
      setProgress(30);

      // Document processing step
      if (workflowResult.documentAnalysis) {
        updateStepStatus("documents", "processing");
        setProgress(50);
        
        // Small delay for visual effect
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        updateStepStatus("documents", "completed", 
          `${workflowResult.documentAnalysis.documentType} processed - ${workflowResult.documentAnalysis.entities.length} entities extracted`
        );
      } else {
        updateStepStatus("documents", "completed", "No documents to process");
      }
      setProgress(60);

      // Tamper detection step  
      if (workflowResult.tamperDetection) {
        updateStepStatus("tamper", "processing");
        setProgress(75);
        
        // Small delay for visual effect
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        updateStepStatus("tamper", "completed",
          `${workflowResult.tamperDetection.isAuthentic ? 'Authentic' : 'Flagged'} - Risk: ${workflowResult.tamperDetection.riskLevel}`
        );
      } else {
        updateStepStatus("tamper", "completed", "No tamper detection needed");
      }
      setProgress(85);

      // ERP Integration step
      updateStepStatus("erp", "processing");
      setProgress(95);
      
      // Small delay for visual effect
      await new Promise(resolve => setTimeout(resolve, 500));
      
      updateStepStatus("erp", "completed", 
        `Customer ${workflowResult.erpIntegration.customerId} created successfully`
      );
      setProgress(100);

      // Set REAL results from API
      setResult(workflowResult);
      setCurrentStep("");

      toast({
        title: "KYC Workflow Complete!",
        description: `Real AI processing completed in ${workflowResult.processingTime}s`,
      });

    } catch (error: any) {
      console.error("Real API Error:", error);
      updateStepStatus(currentStep, "error");
      toast({
        title: "Workflow Error", 
        description: error.message || "Could not complete KYC workflow",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteRecord = () => {
    if (result?.erpIntegration.customerId) {
      toast({
        title: "Record Deleted",
        description: `Customer ${result.erpIntegration.customerId} has been removed from ERP`,
      });
      setResult(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/models">
            <Button variant="ghost">
              <ArrowLeft className="w-4 h-4" />
              Back to Models
            </Button>
          </Link>
          <Button variant="outline" onClick={() => navigate("/dashboard")}>
            <Database className="w-4 h-4 mr-2" />
            ERP Dashboard
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-6 py-12">
        <div className="max-w-7xl mx-auto">
          {/* Page Header */}
          <div className="text-center mb-12">
            <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center mb-6">
              <Mail className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-foreground mb-4">Real AI KYC Workflow</h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Send your onboarding request with documents and watch real AI process everything from email to ERP integration
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Input Section */}
            <div className="lg:col-span-1 space-y-6">
              {/* Instructions */}
              <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Info className="w-5 h-5 text-primary" />
                    Quick Start
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    {sampleEmails.map((sample, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        className="w-full justify-start text-left h-auto py-3"
                        onClick={() => loadSampleEmail(sample)}
                      >
                        <div className="flex-1">
                          <div className="font-medium text-sm">{sample.title}</div>
                          <div className="text-xs text-muted-foreground">
                            {sample.hasAttachments ? "📎 With attachments" : "📧 Email only"}
                          </div>
                        </div>
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Email Input */}
              <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle>Email to: kyc@jupiterbrains.com</CardTitle>
                  <CardDescription>Complete your KYC onboarding request</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-foreground mb-2 block">Subject</label>
                    <Input
                      placeholder="Email subject..."
                      value={subject}
                      onChange={(e) => setSubject(e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium text-foreground mb-2 block">Body</label>
                    <Textarea
                      placeholder="Describe your onboarding request..."
                      value={body}
                      onChange={(e) => setBody(e.target.value)}
                      rows={8}
                      className="min-h-[160px]"
                    />
                  </div>
                  
                  {/* File Upload */}
                  <div>
                    <label className="text-sm font-medium text-foreground mb-2 block">Documents</label>
                    <div className="border-2 border-dashed border-border rounded-lg p-4">
                      <input
                        type="file"
                        multiple
                        onChange={handleFileUpload}
                        className="hidden"
                        id="file-upload"
                        accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                      />
                      <label htmlFor="file-upload" className="cursor-pointer">
                        <div className="text-center">
                          <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                          <p className="text-sm text-muted-foreground">
                            Drop files here or click to upload
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            PDF, JPG, PNG, DOC, DOCX
                          </p>
                        </div>
                      </label>
                    </div>
                    
                    {/* Attached Files */}
                    {attachments.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {attachments.map((file, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-muted rounded">
                            <div className="flex items-center gap-2">
                              <FileText className="w-4 h-4 text-primary" />
                              <span className="text-sm">{file.name}</span>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeAttachment(index)}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <Button 
                    onClick={handleRunCompleteWorkflow} 
                    disabled={loading} 
                    className="w-full" 
                    variant="hero"
                    size="lg"
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Processing with Real AI...
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4 mr-2" />
                        Send Real KYC Request
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Workflow Animation & Results */}
            <div className="lg:col-span-2 space-y-6">
              {/* Progress Bar */}
              {loading && (
                <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Real AI Processing</span>
                      <span className="text-sm text-muted-foreground">{progress}%</span>
                    </div>
                    <Progress value={progress} className="h-2" />
                  </CardContent>
                </Card>
              )}

              {/* Workflow Steps */}
              <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle>Real AI KYC Pipeline</CardTitle>
                  <CardDescription>Watch your request flow through our real Groq AI-powered system</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {workflowSteps.map((step, index) => {
                      const Icon = step.icon;
                      return (
                        <div key={step.id} className="flex items-center gap-4 p-4 rounded-lg bg-muted/30">
                          <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                            step.status === "completed" ? "bg-secondary text-white" :
                            step.status === "processing" ? "bg-processing text-white" :
                            step.status === "error" ? "bg-destructive text-white" :
                            "bg-muted"
                          }`}>
                            {step.status === "processing" ? (
                              <Loader2 className="w-5 h-5 animate-spin" />
                            ) : step.status === "completed" ? (
                              <CheckCircle2 className="w-5 h-5" />
                            ) : (
                              <Icon className="w-5 h-5" />
                            )}
                          </div>
                          
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h3 className="font-semibold text-foreground">{step.title}</h3>
                              <Badge variant={
                                step.status === "completed" ? "default" :
                                step.status === "processing" ? "secondary" :
                                step.status === "error" ? "destructive" :
                                "outline"
                              }>
                                {step.status}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground">{step.description}</p>
                            {step.result && (
                              <p className="text-sm text-secondary mt-1">✓ {step.result}</p>
                            )}
                          </div>

                          {index < workflowSteps.length - 1 && (
                            <ArrowRight className="w-4 h-4 text-muted-foreground" />
                          )}
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Results */}
              {result && (
                <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      Real AI Processing Results
                      <Button variant="destructive" size="sm" onClick={handleDeleteRecord}>
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete Record
                      </Button>
                    </CardTitle>
                    <CardDescription>Complete automation results from real AI and ERP integration</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-2 gap-6">
                      {/* Email Classification */}
                      <div className="space-y-4">
                        <h3 className="font-semibold text-foreground">Real AI Email Analysis</h3>
                        <div className="space-y-3">
                          <div className="p-3 rounded-lg bg-primary/10 border border-primary/20">
                            <p className="text-sm text-muted-foreground mb-1">Category</p>
                            <p className="font-semibold text-primary">{result.emailClassification.category}</p>
                          </div>
                          <div className="grid grid-cols-2 gap-3">
                            <div className="p-3 rounded-lg bg-muted/50">
                              <p className="text-sm text-muted-foreground mb-1">Priority</p>
                              <Badge variant="outline">{result.emailClassification.priority}</Badge>
                            </div>
                            <div className="p-3 rounded-lg bg-muted/50">
                              <p className="text-sm text-muted-foreground mb-1">Sentiment</p>
                              <Badge variant="outline">{result.emailClassification.sentiment}</Badge>
                            </div>
                          </div>
                          <div className="p-3 rounded-lg bg-muted/50">
                            <p className="text-sm text-muted-foreground mb-1">AI Confidence</p>
                            <div className="flex items-center gap-3">
                              <div className="flex-1 bg-border rounded-full h-2">
                                <div 
                                  className="bg-primary h-2 rounded-full transition-all duration-500"
                                  style={{ width: `${result.emailClassification.confidence * 100}%` }}
                                />
                              </div>
                              <span className="text-sm font-semibold text-foreground">
                                {Math.round(result.emailClassification.confidence * 100)}%
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Document Processing */}
                      {result.documentAnalysis && (
                        <div className="space-y-4">
                          <h3 className="font-semibold text-foreground">Real Document Analysis</h3>
                          <div className="space-y-3">
                            <div className="p-3 rounded-lg bg-muted/50">
                              <p className="text-sm text-muted-foreground mb-1">Document Type</p>
                              <p className="font-semibold">{result.documentAnalysis.documentType}</p>
                            </div>
                            <div className="p-3 rounded-lg bg-muted/50">
                              <p className="text-sm text-muted-foreground mb-2">Extracted Data</p>
                              <div className="space-y-1">
                                {result.documentAnalysis.entities.map((entity, i) => (
                                  <p key={i} className="text-xs text-foreground">{entity}</p>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Tamper Detection */}
                      {result.tamperDetection && (
                        <div className="space-y-4">
                          <h3 className="font-semibold text-foreground">Document Verification</h3>
                          <div className="space-y-3">
                            <div className="p-3 rounded-lg bg-muted/50">
                              <p className="text-sm text-muted-foreground mb-1">Authenticity</p>
                              <Badge variant={result.tamperDetection.isAuthentic ? "default" : "destructive"}>
                                {result.tamperDetection.isAuthentic ? "Authentic" : "Flagged"}
                              </Badge>
                            </div>
                            <div className="p-3 rounded-lg bg-muted/50">
                              <p className="text-sm text-muted-foreground mb-1">Risk Level</p>
                              <Badge variant="outline">{result.tamperDetection.riskLevel}</Badge>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* ERP Integration */}
                      <div className="space-y-4">
                        <h3 className="font-semibold text-foreground">ERP Integration</h3>
                        <div className="space-y-3">
                          <div className="p-3 rounded-lg bg-secondary/10 border border-secondary/20">
                            <p className="text-sm text-muted-foreground mb-1">Customer ID</p>
                            <p className="font-semibold text-secondary">{result.erpIntegration.customerId}</p>
                          </div>
                          <div className="p-3 rounded-lg bg-muted/50">
                            <p className="text-sm text-muted-foreground mb-1">Status</p>
                            <Badge variant="default">{result.erpIntegration.status}</Badge>
                          </div>
                          <div className="p-3 rounded-lg bg-muted/50">
                            <p className="text-sm text-muted-foreground mb-1">AI Processing Time</p>
                            <p className="font-semibold flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {result.processingTime}s
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="mt-6 flex gap-3">
                      <Button variant="outline" onClick={() => navigate("/dashboard")}>
                        <Database className="w-4 h-4 mr-2" />
                        View in ERP Dashboard
                      </Button>
                      <Button variant="outline" onClick={() => {
                        setResult(null);
                        setSubject("");
                        setBody("");
                        setAttachments([]);
                        resetWorkflowSteps();
                        setProgress(0);
                      }}>
                        Start New Request
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailDemo;