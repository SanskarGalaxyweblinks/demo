import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { MessageSquare, ArrowLeft, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const ResponseDemo = () => {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleGenerate = async () => {
    if (!input) {
      toast({
        title: "Missing Input",
        description: "Please provide email content to generate a response",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    // Simulate AI processing
    setTimeout(() => {
      setResponse(
        "Dear Valued Customer,\n\nThank you for reaching out to us. We have received your inquiry and our team is currently reviewing your request.\n\nWe will get back to you within 24 hours with a detailed response.\n\nBest regards,\nJupiterBrains Support Team"
      );
      setLoading(false);
      toast({
        title: "Response Generated",
        description: "AI has created a contextual response",
      });
    }, 2000);
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
            <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-processing to-[hsl(45,93%,47%)] flex items-center justify-center">
              <MessageSquare className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">Automated Response Generator</h1>
              <p className="text-muted-foreground">Generate policy-compliant responses automatically</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Input Section */}
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Input Message</CardTitle>
                <CardDescription>Paste the email content to respond to</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  placeholder="Enter the received email content here..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  rows={15}
                />
                <Button onClick={handleGenerate} disabled={loading} className="w-full" variant="ai">
                  {loading ? "Generating..." : "Generate Response"}
                  <Sparkles className="w-4 h-4" />
                </Button>
              </CardContent>
            </Card>

            {/* Results Section */}
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Generated Response</CardTitle>
                <CardDescription>AI-crafted contextual reply</CardDescription>
              </CardHeader>
              <CardContent>
                {response ? (
                  <div className="p-4 rounded-lg bg-muted/50 min-h-[300px]">
                    <pre className="whitespace-pre-wrap text-sm text-foreground font-sans">
                      {response}
                    </pre>
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    Generate a response to see AI-crafted reply
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

export default ResponseDemo;
