import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Mail, ArrowLeft, Sparkles, Clock, AlignLeft, BrainCircuit, Database, Info } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";

// Define the response structure for KYC classification
interface KYCClassificationResult {
  category: "Onboarding" | "Dispute" | "Other";
  priority: "High" | "Medium" | "Low";
  sentiment: "Positive" | "Negative" | "Neutral";
  confidence: number;
  tags: string[];
  processing_time: number;
}

const EmailDemo = () => {
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [result, setResult] = useState<KYCClassificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const { token } = useAuth();
  const navigate = useNavigate();

  // Sample emails for easy testing
  const sampleEmails = [
    {
      title: "Onboarding Request",
      subject: "New Customer Application - John Smith",
      body: "Hello, I would like to open a new account and complete the KYC process. I have attached my driver's license and bank statement. Please let me know what other documents you need."
    },
    {
      title: "Dispute Email", 
      subject: "Account Verification Dispute",
      body: "I'm writing to dispute the rejection of my account verification. The documents I submitted are legitimate and I believe there was an error in the review process."
    },
    {
      title: "General Inquiry",
      subject: "Question about services",
      body: "Can you please provide more information about your account features and fees? I'm comparing different options."
    }
  ];

  const loadSampleEmail = (sample: typeof sampleEmails[0]) => {
    setSubject(sample.subject);
    setBody(sample.body);
    setResult(null);
  };

  const handleRunModel = async () => {
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

    try {
      // Use environment variable or default to local backend
      const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

      const response = await fetch(`${API_BASE}/emails/classify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { "Authorization": `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          subject,
          body
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        
        if (response.status === 403 && errorData.detail.includes("Usage limit exceeded")) {
            toast({
                title: "Limit Reached",
                description: errorData.detail,
                variant: "destructive",
            });
            return;
        }

        throw new Error(errorData.detail || "Failed to classify email");
      }

      const data: KYCClassificationResult = await response.json();
      setResult(data);

      toast({
        title: "Classification Complete",
        description: `Email classified as ${data.category} with ${(data.confidence * 100).toFixed(1)}% confidence`,
      });

    } catch (error: any) {
      console.error("API Error:", error);
      toast({
        title: "Error", 
        description: error.message || "Could not connect to the classification service",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Header with ERP Button */}
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
          <div className="flex items-center gap-4 mb-8">
            <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-primary to-[hsl(195,100%,45%)] flex items-center justify-center">
              <Mail className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">KYC Email Classifier</h1>
              <p className="text-muted-foreground">Automatically classify customer emails into Onboarding, Dispute, or Other categories</p>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Instructions Panel */}
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="w-5 h-5 text-primary" />
                  Instructions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold text-foreground mb-2">How it works:</h3>
                  <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                    <li>Enter email subject and body</li>
                    <li>Click "Run Classification"</li>
                    <li>View results and confidence score</li>
                    <li>Data automatically goes to ERP</li>
                  </ol>
                </div>

                <div>
                  <h3 className="font-semibold text-foreground mb-2">Sample Emails:</h3>
                  <div className="space-y-2">
                    {sampleEmails.map((sample, index) => (
                      <Button
                        key={index}
                        variant="outline"
                        size="sm"
                        className="w-full justify-start text-left h-auto py-2"
                        onClick={() => loadSampleEmail(sample)}
                      >
                        <div>
                          <div className="font-medium">{sample.title}</div>
                          <div className="text-xs text-muted-foreground truncate">
                            {sample.subject}
                          </div>
                        </div>
                      </Button>
                    ))}
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-primary/10 border border-primary/20">
                  <h3 className="font-semibold text-primary mb-1">Categories:</h3>
                  <div className="space-y-1 text-sm">
                    <div><Badge variant="outline">Onboarding</Badge> - New customer requests</div>
                    <div><Badge variant="outline">Dispute</Badge> - Verification issues</div>
                    <div><Badge variant="outline">Other</Badge> - General inquiries</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Input Section */}
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Test Email Input</CardTitle>
                <CardDescription>Enter customer email details to classify</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">
                    To: kyc@jupiterbrains.com
                  </label>
                </div>
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
                    placeholder="Email content..."
                    value={body}
                    onChange={(e) => setBody(e.target.value)}
                    rows={10}
                    className="min-h-[200px]"
                  />
                </div>
                <Button onClick={handleRunModel} disabled={loading} className="w-full" variant="hero">
                  {loading ? "Processing..." : "Run Classification"}
                  <Sparkles className="w-4 h-4 ml-2" />
                </Button>
              </CardContent>
            </Card>

            {/* Results Section */}
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Classification Results</CardTitle>
                <CardDescription>AI-powered KYC email analysis</CardDescription>
              </CardHeader>
              <CardContent>
                {result ? (
                  <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {/* Main Category */}
                    <div className="p-4 rounded-lg bg-primary/10 border border-primary/20">
                      <p className="text-sm text-muted-foreground mb-1 flex items-center gap-2">
                        <BrainCircuit className="w-4 h-4" /> Category
                      </p>
                      <p className="text-2xl font-bold text-primary">{result.category}</p>
                    </div>

                    {/* Priority & Sentiment */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 rounded-lg bg-muted/50">
                        <p className="text-sm text-muted-foreground mb-1">Priority</p>
                        <Badge variant="outline" className={
                          result.priority === "High" ? "border-destructive text-destructive" :
                          result.priority === "Medium" ? "border-processing text-processing" :
                          "border-secondary text-secondary"
                        }>
                          {result.priority}
                        </Badge>
                      </div>
                      <div className="p-3 rounded-lg bg-muted/50">
                        <p className="text-sm text-muted-foreground mb-1">Sentiment</p>
                        <Badge variant="outline">{result.sentiment}</Badge>
                      </div>
                    </div>

                    {/* Confidence */}
                    <div className="p-4 rounded-lg bg-muted/50">
                      <p className="text-sm text-muted-foreground mb-2">Confidence Score</p>
                      <div className="flex items-center gap-3">
                        <div className="flex-1 bg-border rounded-full h-2">
                          <div 
                            className="bg-primary h-2 rounded-full transition-all duration-500"
                            style={{ width: `${result.confidence * 100}%` }}
                          />
                        </div>
                        <span className="text-lg font-semibold text-foreground">
                          {(result.confidence * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>

                    {/* Tags */}
                    {result.tags.length > 0 && (
                      <div className="p-4 rounded-lg bg-muted/50">
                        <p className="text-sm text-muted-foreground mb-2">Detected Tags</p>
                        <div className="flex flex-wrap gap-1">
                          {result.tags.map((tag, index) => (
                            <Badge key={index} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Stats */}
                    <div className="p-3 rounded-lg bg-muted/50">
                      <p className="text-xs text-muted-foreground mb-1 flex items-center gap-1">
                        <Clock className="w-3 h-3" /> Processing Time
                      </p>
                      <p className="text-lg font-semibold text-foreground">
                        {result.processing_time}s
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-12 text-muted-foreground min-h-[300px]">
                    <BrainCircuit className="w-12 h-12 mb-4 opacity-20" />
                    <p className="text-center">
                      Run the classification to see results.<br/>
                      <span className="text-xs">Try one of the sample emails to get started!</span>
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailDemo;