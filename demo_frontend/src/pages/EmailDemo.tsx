import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Mail, ArrowLeft, Sparkles, Clock, AlignLeft, BrainCircuit } from "lucide-react";
import { Link } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";

// Define the response structure based on your backend model
interface ClassificationResult {
  category: string;
  reasoning: string;
  summary: string;
  processing_time: number;
}

const EmailDemo = () => {
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [result, setResult] = useState<ClassificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const { token } = useAuth();// Get user session for auth token

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
          // Include the token if you decide to protect this route later
          ...(token ? { "Authorization": `Bearer ${token}` } : {})
        },
        body: JSON.stringify({
          subject,
          body
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to classify email");
      }

      const data: ClassificationResult = await response.json();
      setResult(data);

      toast({
        title: "Classification Complete",
        description: `Processed in ${data.processing_time}s`,
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
      <div className="container mx-auto px-6 py-12">
        <Link to="/models">
          <Button variant="ghost" className="mb-6">
            <ArrowLeft className="w-4 h-4" />
            Back to Models
          </Button>
        </Link>

        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-primary to-[hsl(195,100%,45%)] flex items-center justify-center">
              <Mail className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">Email Classifier</h1>
              <p className="text-muted-foreground">Intelligent email categorization powered by LLMs</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Input Section */}
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm h-fit">
              <CardHeader>
                <CardTitle>Input Email</CardTitle>
                <CardDescription>Enter the email details to classify</CardDescription>
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
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm h-fit">
              <CardHeader>
                <CardTitle>Classification Results</CardTitle>
                <CardDescription>AI-powered email analysis</CardDescription>
              </CardHeader>
              <CardContent>
                {result ? (
                  <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {/* Main Category */}
                    <div className="p-4 rounded-lg bg-primary/10 border border-primary/20">
                      <p className="text-sm text-muted-foreground mb-1 flex items-center gap-2">
                        <BrainCircuit className="w-4 h-4" /> Predicted Category
                      </p>
                      <p className="text-2xl font-bold text-primary">{result.category}</p>
                    </div>

                    {/* Summary */}
                    <div className="p-4 rounded-lg bg-muted/50">
                      <p className="text-sm text-muted-foreground mb-2 flex items-center gap-2">
                        <AlignLeft className="w-4 h-4" /> Content Summary
                      </p>
                      <p className="text-sm text-foreground leading-relaxed">
                        {result.summary}
                      </p>
                    </div>

                    {/* Reasoning */}
                    <div className="p-4 rounded-lg bg-muted/50">
                      <p className="text-sm text-muted-foreground mb-2">AI Reasoning</p>
                      <p className="text-sm text-foreground/80 italic border-l-2 border-primary/50 pl-3">
                        "{result.reasoning}"
                      </p>
                    </div>

                    {/* Stats */}
                    <div className="flex gap-4">
                      <div className="p-3 rounded-lg bg-muted/50 flex-1">
                        <p className="text-xs text-muted-foreground mb-1 flex items-center gap-1">
                          <Clock className="w-3 h-3" /> Processing Time
                        </p>
                        <p className="text-lg font-semibold text-foreground">
                          {result.processing_time}s
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-12 text-muted-foreground min-h-[300px]">
                    <BrainCircuit className="w-12 h-12 mb-4 opacity-20" />
                    <p>Run the model to see classification results</p>
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