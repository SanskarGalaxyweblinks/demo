import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { FileText, ArrowLeft, Sparkles, Upload, ReceiptText, Calendar, DollarSign, Building, Database, Info, User, CreditCard } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";
import { cn } from "@/lib/utils";

// Updated interfaces for KYC document extraction
interface PIIExtractionData {
    fullName: string;
    dateOfBirth: string;
    documentNumber: string;
    documentType: string;
    expiryDate: string;
    issuingAuthority: string;
    address: string;
    confidenceScore: number;
}

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
    documentType: "ID_Document" | "Invoice" | "Bank_Statement" | "Other";
    pageCount: number;
    entities: string[];
    detectedCurrency: string | null;
    confidence: number;
    receivedAt: string;
    preview: string | null;
    extractedData: PIIExtractionData | InvoiceExtractionData | null;
}

const DocumentDemo = () => {
    const [file, setFile] = useState<File | null>(null);
    const [result, setResult] = useState<DocumentAnalysisResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const { toast } = useToast();
    const { token } = useAuth();
    const navigate = useNavigate();

    // Sample documents information
    const supportedDocuments = [
        { type: "Driver License", description: "Extract name, DOB, license number, address" },
        { type: "Passport", description: "Extract name, DOB, passport number, nationality" },
        { type: "Invoices", description: "Extract company details, amounts, dates" },
        { type: "Bank Statements", description: "Extract account details, transactions" }
    ];

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setResult(null);
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
                    ...(token ? { "Authorization": `Bearer ${token}` } : {})
                },
                body: formData,
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

                throw new Error(errorData.detail || "Failed to analyze document");
            }

            const data: DocumentAnalysisResponse = await response.json();
            setResult(data);
            
            toast({
                title: "Processing Complete",
                description: `Document analyzed and data extracted for KYC`,
            });

        } catch (error: any) {
            console.error("API Error:", error);
            toast({
                title: "Analysis Error",
                description: error.message || "Could not connect to the analysis service.",
                variant: "destructive",
            });
        } finally {
            setLoading(false);
        }
    };

    // Helper Components for Results Display
    const DataBox = ({ icon: Icon, label, value, color }: { icon?: any, label: string, value: string, color?: string }) => (
        <div className="p-3 rounded-lg bg-muted/50 border border-border/50">
            <p className="text-sm text-muted-foreground mb-1 flex items-center gap-1">
                {Icon && <Icon className={cn("w-4 h-4", color || "text-primary")} />}
                {label}
            </p>
            <p className="text-base font-semibold text-foreground">{value || "Not detected"}</p>
        </div>
    );

    const RenderPIIData = ({ data }: { data: PIIExtractionData }) => (
        <div className="space-y-4">
            <h3 className="text-xl font-bold text-foreground flex items-center gap-2 border-b border-primary/20 pb-2">
                <User className="w-5 h-5 text-secondary" /> Extracted PII Data
            </h3>

            <div className="grid grid-cols-2 gap-4">
                <DataBox icon={User} label="Full Name" value={data.fullName} />
                <DataBox icon={Calendar} label="Date of Birth" value={data.dateOfBirth} />
            </div>

            <div className="grid grid-cols-2 gap-4">
                <DataBox icon={CreditCard} label="Document Number" value={data.documentNumber} />
                <DataBox icon={FileText} label="Document Type" value={data.documentType} />
            </div>

            <DataBox icon={Building} label="Address" value={data.address} />

            <div className="grid grid-cols-2 gap-4">
                <DataBox icon={Calendar} label="Expiry Date" value={data.expiryDate} />
                <DataBox icon={Building} label="Issuing Authority" value={data.issuingAuthority} />
            </div>

            <div className="p-4 rounded-lg bg-secondary/10 border border-secondary/20">
                <p className="text-sm text-muted-foreground mb-2">Extraction Confidence</p>
                <div className="flex items-center gap-3">
                    <div className="flex-1 bg-border rounded-full h-2">
                        <div 
                            className="bg-secondary h-2 rounded-full transition-all duration-500"
                            style={{ width: `${data.confidenceScore * 100}%` }}
                        />
                    </div>
                    <span className="text-lg font-semibold text-foreground">
                        {(data.confidenceScore * 100).toFixed(1)}%
                    </span>
                </div>
            </div>
        </div>
    );

    const RenderInvoiceData = ({ data }: { data: InvoiceExtractionData }) => (
        <div className="space-y-4">
            <h3 className="text-xl font-bold text-foreground flex items-center gap-2 border-b border-primary/20 pb-2">
                <ReceiptText className="w-5 h-5 text-secondary" /> Extracted Invoice Data
            </h3>

            <div className="grid grid-cols-2 gap-4">
                <DataBox icon={ReceiptText} label="Invoice Number" value={data.invoiceNumber} />
                <DataBox icon={Calendar} label="Invoice Date" value={data.invoiceDate} />
            </div>

            <DataBox icon={Building} label="Issuing Company" value={data.issuingCompany} />
            <DataBox icon={Building} label="Bill-To Company" value={data.billToCompany} />

            <div className="grid grid-cols-2 gap-4">
                <DataBox 
                    icon={DollarSign} 
                    label="Total Amount" 
                    value={`${data.currency} ${data.totalAmount.toFixed(2)}`} 
                    color="text-secondary"
                />
                <DataBox label="Language" value={data.language.toUpperCase()} />
            </div>

            {data.customerPO && (
                <DataBox label="Customer PO" value={data.customerPO} />
            )}
        </div>
    );

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
                        <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-secondary to-[hsl(158,64%,42%)] flex items-center justify-center">
                            <FileText className="w-7 h-7 text-white" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold text-foreground">Document Extractor</h1>
                            <p className="text-muted-foreground">Extract critical PII and invoice data from customer documents</p>
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
                                        <li>Upload a document (PDF, image, DOCX)</li>
                                        <li>Click "Analyze Document"</li>
                                        <li>View extracted PII or invoice data</li>
                                        <li>Data automatically goes to ERP</li>
                                    </ol>
                                </div>

                                <div>
                                    <h3 className="font-semibold text-foreground mb-2">Supported Documents:</h3>
                                    <div className="space-y-2">
                                        {supportedDocuments.map((doc, index) => (
                                            <div key={index} className="p-2 rounded-lg bg-muted/50 border border-border/30">
                                                <div className="font-medium text-sm">{doc.type}</div>
                                                <div className="text-xs text-muted-foreground">{doc.description}</div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div className="p-3 rounded-lg bg-secondary/10 border border-secondary/20">
                                    <h3 className="font-semibold text-secondary mb-1">Data Extracted:</h3>
                                    <div className="space-y-1 text-sm">
                                        <div><Badge variant="outline">PII</Badge> - Names, DOB, addresses</div>
                                        <div><Badge variant="outline">Financial</Badge> - Invoice amounts, dates</div>
                                        <div><Badge variant="outline">Identity</Badge> - Document numbers</div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Upload Section */}
                        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
                            <CardHeader>
                                <CardTitle>Upload Document</CardTitle>
                                <CardDescription>Upload customer documents for KYC data extraction</CardDescription>
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
                                        <div className="mt-4 p-3 bg-primary/10 rounded-lg">
                                            <p className="text-sm text-foreground">
                                                Selected: <span className="font-medium">{file.name}</span>
                                            </p>
                                            <p className="text-xs text-muted-foreground">
                                                Size: {(file.size / 1024).toFixed(1)} KB
                                            </p>
                                        </div>
                                    )}
                                </div>
                                <Button onClick={handleRunModel} disabled={loading || !file} className="w-full" variant="hero">
                                    {loading ? "Processing..." : "Analyze Document"}
                                    <Sparkles className="w-4 h-4 ml-2" />
                                </Button>
                            </CardContent>
                        </Card>

                        {/* Results Section */}
                        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
                            <CardHeader>
                                <CardTitle>Extraction Results</CardTitle>
                                <CardDescription>Extracted KYC data and document analysis</CardDescription>
                            </CardHeader>
                            <CardContent>
                                {result ? (
                                    <div className="space-y-6">
                                        {/* Document Type Badge */}
                                        <div className="flex items-center justify-between">
                                            <Badge variant="outline" className="text-sm py-1 px-3">
                                                {result.documentType.replace('_', ' ')}
                                            </Badge>
                                            <span className="text-xs text-muted-foreground">
                                                {result.pageCount} pages
                                            </span>
                                        </div>

                                        {/* Extracted Data */}
                                        {result.extractedData ? (
                                            result.documentType === "ID_Document" ? (
                                                <RenderPIIData data={result.extractedData as PIIExtractionData} />
                                            ) : (
                                                <RenderInvoiceData data={result.extractedData as InvoiceExtractionData} />
                                            )
                                        ) : (
                                            <div className="p-4 rounded-lg bg-processing/10 border border-processing/50">
                                                <p className="text-processing font-medium">
                                                    Document processed but specific data extraction failed.
                                                </p>
                                            </div>
                                        )}

                                        {/* Additional Entities */}
                                        {result.entities.length > 0 && (
                                            <div className="p-4 rounded-lg bg-muted/50">
                                                <p className="text-sm text-muted-foreground mb-2">Additional Detected Entities</p>
                                                <div className="flex flex-wrap gap-2">
                                                    {result.entities.map((entity: string, idx: number) => (
                                                        <Badge key={idx} variant="secondary" className="text-xs">
                                                            {entity}
                                                        </Badge>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center py-12 text-muted-foreground min-h-[300px]">
                                        <FileText className="w-12 h-12 mb-4 opacity-20" />
                                        <p className="text-center">
                                            Upload a document to extract KYC data.<br/>
                                            <span className="text-xs">Supports IDs, invoices, and bank statements.</span>
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

export default DocumentDemo;