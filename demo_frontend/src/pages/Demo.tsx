import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Mail,
  FileText,
  Brain,
  Send,
  Database,
  CheckCircle2,
  Upload,
  Loader2,
  ArrowLeft,
  Sparkles,
  FileUp
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

interface ProcessingStep {
  id: string;
  title: string;
  icon: any;
  status: "pending" | "processing" | "completed" | "error";
  result?: string;
  details?: string;
}

const Demo = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [emailSubject, setEmailSubject] = useState("");
  const [emailBody, setEmailBody] = useState("");
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [steps, setSteps] = useState<ProcessingStep[]>([
    {
      id: "classify",
      title: "Email Classification",
      icon: Brain,
      status: "pending",
    },
    {
      id: "extract",
      title: "Document Extraction",
      icon: FileText,
      status: "pending",
    },
    {
      id: "analyze",
      title: "Content Analysis",
      icon: Sparkles,
      status: "pending",
    },
    {
      id: "response",
      title: "Response Generation",
      icon: Send,
      status: "pending",
    },
    {
      id: "erp",
      title: "ERP Integration",
      icon: Database,
      status: "pending",
    },
  ]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setAttachments([...attachments, ...newFiles]);
      toast({
        title: "Files added",
        description: `${newFiles.length} file(s) added to your email`,
      });
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments(attachments.filter((_, i) => i !== index));
  };

  const simulateProcessing = async () => {
    if (!emailSubject || !emailBody) {
      toast({
        title: "Missing information",
        description: "Please enter both subject and email body",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);
    setProgress(0);

    // Reset steps
    setSteps(steps.map(step => ({ ...step, status: "pending", result: undefined, details: undefined })));

    // Step 1: Email Classification
    await processStep(0, {
      result: "Support Request - Technical Issue",
      details: "Category: Technical Support | Priority: High | Sentiment: Neutral",
    });
    setProgress(20);

    // Step 2: Document Extraction
    await processStep(1, {
      result: attachments.length > 0 ? `Extracted ${attachments.length} document(s)` : "No attachments to process",
      details: attachments.length > 0 
        ? `Files: ${attachments.map(f => f.name).join(", ")}`
        : "Proceeding without document extraction",
    });
    setProgress(40);

    // Step 3: Content Analysis
    await processStep(2, {
      result: "Key entities identified",
      details: "Detected: Product inquiry, pricing questions, integration requirements",
    });
    setProgress(60);

    // Step 4: Response Generation
    await processStep(3, {
      result: "Automated response drafted",
      details: "Response includes: Pricing information, integration guide links, next steps",
    });
    setProgress(80);

    // Step 5: ERP Integration
    await processStep(4, {
      result: "ERP entry created",
      details: "Ticket #12847 created | Assigned to: Support Team | SLA: 24 hours",
    });
    setProgress(100);

    setIsProcessing(false);
    toast({
      title: "Processing complete!",
      description: "Your email has been successfully processed",
    });
  };

  const processStep = async (index: number, result: { result: string; details: string }) => {
    // Set to processing
    setSteps(prev => prev.map((step, i) => 
      i === index ? { ...step, status: "processing" } : step
    ));

    // Simulate processing time
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Set to completed with results
    setSteps(prev => prev.map((step, i) => 
      i === index ? { ...step, status: "completed", ...result } : step
    ));
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="w-5 h-5 text-secondary" />;
      case "processing":
        return <Loader2 className="w-5 h-5 text-processing animate-spin" />;
      case "error":
        return <CheckCircle2 className="w-5 h-5 text-destructive" />;
      default:
        return <div className="w-5 h-5 rounded-full border-2 border-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-secondary/10 border-secondary/20";
      case "processing":
        return "bg-processing/10 border-processing/20";
      case "error":
        return "bg-destructive/10 border-destructive/20";
      default:
        return "bg-muted border-border";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate("/")}
              >
                <ArrowLeft className="w-4 h-4" />
                Back
              </Button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-foreground">Interactive Demo</h1>
                  <p className="text-xs text-muted-foreground">Test the AI Email Classification System</p>
                </div>
              </div>
            </div>
            <Button variant="outline" size="sm" onClick={() => navigate("/dashboard")}>
              View Dashboard
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Email Composer */}
          <div className="space-y-6">
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="w-5 h-5 text-primary" />
                  Compose Test Email
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">
                    To: demoemail@jupiterbrains.com
                  </label>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">
                    Subject
                  </label>
                  <Input
                    placeholder="Enter email subject..."
                    value={emailSubject}
                    onChange={(e) => setEmailSubject(e.target.value)}
                    disabled={isProcessing}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">
                    Message Body
                  </label>
                  <Textarea
                    placeholder="Enter your email message..."
                    value={emailBody}
                    onChange={(e) => setEmailBody(e.target.value)}
                    className="min-h-[200px]"
                    disabled={isProcessing}
                  />
                </div>

                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">
                    Attachments
                  </label>
                  <div className="space-y-2">
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => document.getElementById("file-upload")?.click()}
                      disabled={isProcessing}
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Add Attachments
                    </Button>
                    <input
                      id="file-upload"
                      type="file"
                      multiple
                      className="hidden"
                      onChange={handleFileUpload}
                      disabled={isProcessing}
                    />
                    
                    {attachments.length > 0 && (
                      <div className="space-y-2">
                        {attachments.map((file, index) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-2 rounded-lg border border-border bg-muted/50"
                          >
                            <div className="flex items-center gap-2">
                              <FileUp className="w-4 h-4 text-primary" />
                              <span className="text-sm text-foreground">{file.name}</span>
                              <span className="text-xs text-muted-foreground">
                                ({(file.size / 1024).toFixed(1)} KB)
                              </span>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeAttachment(index)}
                              disabled={isProcessing}
                            >
                              Remove
                            </Button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                <Button
                  className="w-full"
                  size="lg"
                  onClick={simulateProcessing}
                  disabled={isProcessing}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4 mr-2" />
                      Send & Process
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Processing Pipeline */}
          <div className="space-y-6">
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-primary" />
                  Processing Pipeline
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {isProcessing && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Overall Progress</span>
                      <span className="font-medium text-foreground">{progress}%</span>
                    </div>
                    <Progress value={progress} className="h-2" />
                  </div>
                )}

                <div className="space-y-4">
                  {steps.map((step, index) => {
                    const Icon = step.icon;
                    return (
                      <div key={step.id}>
                        <div className={`p-4 rounded-lg border transition-all ${getStatusColor(step.status)}`}>
                          <div className="flex items-start gap-4">
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${
                              step.status === "completed" 
                                ? "bg-secondary/20" 
                                : step.status === "processing" 
                                ? "bg-processing/20" 
                                : "bg-muted"
                            }`}>
                              <Icon className={`w-6 h-6 ${
                                step.status === "completed" 
                                  ? "text-secondary" 
                                  : step.status === "processing" 
                                  ? "text-processing" 
                                  : "text-muted-foreground"
                              }`} />
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-semibold text-foreground">{step.title}</h3>
                                {step.status !== "pending" && (
                                  <Badge variant="outline" className="capitalize">
                                    {step.status}
                                  </Badge>
                                )}
                              </div>
                              
                              {step.result && (
                                <div className="mt-2 space-y-1">
                                  <p className="text-sm font-medium text-foreground">{step.result}</p>
                                  {step.details && (
                                    <p className="text-xs text-muted-foreground">{step.details}</p>
                                  )}
                                </div>
                              )}
                            </div>

                            <div className="flex-shrink-0">
                              {getStatusIcon(step.status)}
                            </div>
                          </div>
                        </div>
                        
                        {index < steps.length - 1 && (
                          <div className="flex justify-center py-2">
                            <div className="w-0.5 h-6 bg-border" />
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Demo;
