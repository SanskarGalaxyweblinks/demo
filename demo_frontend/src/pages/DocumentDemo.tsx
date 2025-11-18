import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { FileText, ArrowLeft, Sparkles, Upload } from "lucide-react";
import { Link } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const DocumentDemo = () => {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleRunModel = async () => {
    if (!file) {
      toast({
        title: "No File Selected",
        description: "Please upload a document first",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    // Simulate AI processing
    setTimeout(() => {
      setResult({
        type: "Invoice",
        extractedText: "Sample extracted content from the document...",
        entities: ["Company Name", "Invoice #12345", "$2,500.00"],
        confidence: 0.92
      });
      setLoading(false);
      toast({
        title: "Processing Complete",
        description: "Document has been successfully analyzed",
      });
    }, 2500);
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
            <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-secondary to-[hsl(158,64%,42%)] flex items-center justify-center">
              <FileText className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">Document Classifier</h1>
              <p className="text-muted-foreground">Extract and analyze document content with AI</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Input Section */}
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Upload Document</CardTitle>
                <CardDescription>PDF, DOCX, or image files supported</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
                  <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                  <Input
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                    className="max-w-xs mx-auto"
                  />
                  {file && (
                    <p className="mt-4 text-sm text-foreground">
                      Selected: <span className="font-medium">{file.name}</span>
                    </p>
                  )}
                </div>
                <Button onClick={handleRunModel} disabled={loading} className="w-full" variant="success">
                  {loading ? "Processing..." : "Analyze Document"}
                  <Sparkles className="w-4 h-4" />
                </Button>
              </CardContent>
            </Card>

            {/* Results Section */}
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Analysis Results</CardTitle>
                <CardDescription>Extracted information and insights</CardDescription>
              </CardHeader>
              <CardContent>
                {result ? (
                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-muted/50">
                      <p className="text-sm text-muted-foreground mb-1">Document Type</p>
                      <p className="text-lg font-semibold text-foreground">{result.type}</p>
                    </div>
                    <div className="p-4 rounded-lg bg-muted/50">
                      <p className="text-sm text-muted-foreground mb-2">Extracted Entities</p>
                      <div className="flex flex-wrap gap-2">
                        {result.entities.map((entity: string, idx: number) => (
                          <span key={idx} className="px-3 py-1 bg-secondary/20 text-secondary rounded-full text-sm">
                            {entity}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="p-4 rounded-lg bg-muted/50">
                      <p className="text-sm text-muted-foreground mb-1">Confidence Score</p>
                      <p className="text-lg font-semibold text-foreground">{(result.confidence * 100).toFixed(0)}%</p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    Upload and analyze a document to see results
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

export default DocumentDemo;
