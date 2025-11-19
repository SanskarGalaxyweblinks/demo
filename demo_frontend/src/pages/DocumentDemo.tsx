import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { FileText, ArrowLeft, Sparkles, Upload, ReceiptText, Calendar, DollarSign, Building } from "lucide-react";
import { Link } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";
import { cn } from "@/lib/utils"; // Assuming cn utility is available for styling

// New/Updated Interfaces matching the backend Python models
interface InvoiceExtractionData {
    invoiceNumber: string;
    issuingCompany: string;
    billToCompany: string;
    invoiceDate: string;
    totalAmount: number;
    currency: string;
    customerPO: string | null;
    confidenceScore: string;
    language: string;
}

interface DocumentAnalysisResponse {
    documentType: string;
    pageCount: number;
    entities: string[];
    detectedCurrency: string | null;
    confidence: number;
    receivedAt: string;
    preview: string | null;
    extractedData: InvoiceExtractionData | null; // This is the new key
}

const DocumentDemo = () => {
    const [file, setFile] = useState<File | null>(null);
    const [result, setResult] = useState<DocumentAnalysisResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const { toast } = useToast();
    const { token } = useAuth(); // Get user session for auth token

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
        setResult(null);

        try {
            const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
            
            const formData = new FormData();
            formData.append("file", file);

            const response = await fetch(`${API_BASE}/documents/analyze`, {
                method: "POST",
                headers: {
                    // Include the auth token if available
                    ...(token ? { "Authorization": `Bearer ${token}` } : {})
                },
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json();


                // Handle Usage Limit Specific Error
                if (response.status === 403 && errorData.detail.includes("Usage limit exceeded")) {
                    toast({
                        title: "Limit Reached",
                        description: errorData.detail,
                        variant: "destructive",
                    });
                    return;
                }
                

                throw new Error(errorData.detail || "Failed to analyze document");
            }

            const data: DocumentAnalysisResponse = await response.json();
            setResult(data);
            
            toast({
                title: "Processing Complete",
                description: `Document successfully analyzed as ${data.documentType}`,
            });

        } catch (error: any) {
            console.error("API Error:", error);
            toast({
                title: "Analysis Error",
                description: error.message || "Could not connect to the analysis service or failed to parse response.",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    // --- Helper Components for Results Display ---

    const DataBox = ({ icon: Icon, label, value, color }: { icon?: any, label: string, value: string, color?: string }) => (
        <div className="p-3 rounded-lg bg-muted/50 border border-border/50">
            <p className="text-sm text-muted-foreground mb-1 flex items-center gap-1">
                {Icon && <Icon className={cn("w-4 h-4", color || "text-primary")} />}
                {label}
            </p>
            <p className="text-base font-semibold text-foreground">{value}</p>
        </div>
    );

    const RenderExtractedData = ({ data }: { data: InvoiceExtractionData }) => (
        <div className="space-y-4">
            <h3 className="text-xl font-bold text-foreground flex items-center gap-2 border-b border-primary/20 pb-2">
                <ReceiptText className="w-5 h-5 text-secondary" /> Structured Invoice Data ({data.language.toUpperCase()})
            </h3>

            <div className="grid grid-cols-2 gap-4">
                <DataBox icon={ReceiptText} label="Invoice Number" value={data.invoiceNumber} />
                <DataBox icon={Calendar} label="Invoice Date" value={data.invoiceDate} />
            </div>

            <DataBox icon={Building} label="Issuing Company (Sender)" value={data.issuingCompany} />
            <DataBox icon={Building} label="Bill-To Company (Customer)" value={data.billToCompany} />

            <div className="grid grid-cols-2 gap-4">
                <DataBox 
                    icon={DollarSign} 
                    label="Total Amount" 
                    value={`${data.currency} ${data.totalAmount.toFixed(2)}`} 
                    color="text-secondary"
                />
                <DataBox label="Confidence Score" value={data.confidenceScore.toUpperCase()} />
            </div>
            {data.customerPO && (
                <DataBox label="Customer PO" value={data.customerPO} />
            )}
        </div>
    );

    // --- Main Component Render ---
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
                        <Card className="border-border/50 bg-card/80 backdrop-blur-sm h-fit">
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
                                    <div className="space-y-6">
                                        {result.extractedData ? (
                                            <RenderExtractedData data={result.extractedData} />
                                        ) : (
                                            <div className="p-4 rounded-lg bg-destructive/10 border border-destructive/50 text-destructive font-medium">
                                                Failed to extract structured invoice data. See metadata below.
                                            </div>
                                        )}
                                        
                                        {/* Metadata and Preview (Kept for completeness) */}
                                        <div className="space-y-4 pt-4 border-t border-border/50">
                                            <h3 className="text-lg font-bold text-foreground">
                                                Document Metadata
                                            </h3>

                                            <DataBox icon={FileText} label="Document Type (MIME)" value={result.documentType} />
                                            <DataBox label="Page Count Estimate" value={result.pageCount.toString()} />
                                            
                                            <div className="p-4 rounded-lg bg-muted/50">
                                              <p className="text-sm text-muted-foreground mb-2">Basic Entities (Fallback)</p>
                                              <div className="flex flex-wrap gap-2">
                                                  {result.entities.map((entity: string, idx: number) => (
                                                      <span key={idx} className="px-3 py-1 bg-secondary/20 text-secondary rounded-full text-sm">
                                                          {entity}
                                                      </span>
                                                  ))}
                                              </div>
                                            </div>

                                            {result.preview && (
                                                <div className="p-4 rounded-lg bg-muted/50">
                                                    <p className="text-sm text-muted-foreground mb-1">Text Preview (First 400 Chars)</p>
                                                    <p className="text-xs text-foreground italic whitespace-pre-wrap">{result.preview}...</p>
                                                </div>
                                            )}
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