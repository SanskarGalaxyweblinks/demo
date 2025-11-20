import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Database, ArrowLeft, Sparkles, CheckCircle, AlertTriangle, Info, Building2 } from "lucide-react";
import { Link } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";

interface ErpResult {
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

const ErpDemo = () => {
  const [customerName, setCustomerName] = useState("");
  const [orderAmount, setOrderAmount] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [result, setResult] = useState<ErpResult | null>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const { token } = useAuth();

  const handleIntegrate = async () => {
    if (!customerName || !orderAmount) {
      toast({
        title: "Missing Information",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    if (!token) {
      toast({
        title: "Authentication Required",
        description: "Please log in to sync with ERP",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
      
      const response = await fetch(`${API_BASE}/erp/sync`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          customerName: customerName.trim(),
          orderAmount: parseFloat(orderAmount),
          currency: currency
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to sync with ERP");
      }

      const data: ErpResult = await response.json();
      setResult(data);

      toast({
        title: "Integration Complete",
        description: data.status === "Success" 
          ? "Data has been synced to Odoo ERP system" 
          : "Partial sync completed - check results",
        variant: data.status === "Success" ? "default" : "destructive"
      });

    } catch (error: any) {
      console.error("ERP sync error:", error);
      
      // Create error result
      const errorResult: ErpResult = {
        recordId: `ERROR-${Date.now()}`,
        status: "Error",
        synced: false,
        timestamp: new Date().toISOString(),
        error: error.message || "Failed to connect to ERP system"
      };
      
      setResult(errorResult);
      
      toast({
        title: "Sync Failed",
        description: "Failed to connect to Odoo ERP. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case "Success": return "border-secondary text-secondary bg-secondary/10";
      case "Partial Success": return "border-processing text-processing bg-processing/10";
      case "Error": return "border-destructive text-destructive bg-destructive/10";
      default: return "border-border text-foreground bg-muted/10";
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

        <div className="max-w-6xl mx-auto">
          <div className="flex items-center gap-4 mb-8">
            <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-accent to-[hsl(30,92%,55%)] flex items-center justify-center">
              <Database className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">Odoo ERP Integration Demo</h1>
              <p className="text-muted-foreground">Seamless data synchronization with Odoo ERP system</p>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Information Panel */}
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Info className="w-5 h-5 text-primary" />
                  How It Works
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold text-foreground mb-2">Process:</h3>
                  <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
                    <li>Enter customer information</li>
                    <li>Specify order amount and currency</li>
                    <li>Click "Sync to ERP"</li>
                    <li>Data creates customer + sales lead in Odoo</li>
                  </ol>
                </div>

                <div className="p-3 rounded-lg bg-accent/10 border border-accent/20">
                  <h3 className="font-semibold text-accent mb-2">Odoo Integration:</h3>
                  <div className="space-y-1 text-sm">
                    <div className="flex items-center gap-2">
                      <Building2 className="w-4 h-4" />
                      <span>Creates customer in CRM</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-4 h-4" />
                      <span>Generates sales opportunity</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Database className="w-4 h-4" />
                      <span>Real-time sync to Odoo</span>
                    </div>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-muted/50">
                  <p className="text-xs text-muted-foreground">
                    <strong>Live ERP:</strong> This demo connects to a real Odoo instance.
                    All data will be created in the actual ERP system.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Input Section */}
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Customer Data</CardTitle>
                <CardDescription>Enter information to sync with Odoo ERP</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">Customer Name</label>
                  <Input
                    placeholder="Enter customer name..."
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    disabled={loading}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">Order Amount</label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="Enter order amount..."
                    value={orderAmount}
                    onChange={(e) => setOrderAmount(e.target.value)}
                    disabled={loading}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">Currency</label>
                  <select 
                    value={currency} 
                    onChange={(e) => setCurrency(e.target.value)}
                    className="w-full px-3 py-2 rounded-md border border-input bg-background text-sm"
                    disabled={loading}
                  >
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                    <option value="INR">INR</option>
                  </select>
                </div>
                <Button 
                  onClick={handleIntegrate} 
                  disabled={loading || !customerName || !orderAmount} 
                  className="w-full" 
                  variant="default"
                >
                  {loading ? (
                    <>
                      <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                      Syncing to Odoo...
                    </>
                  ) : (
                    <>
                      <Database className="w-4 h-4 mr-2" />
                      Sync to ERP
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Results Section */}
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Odoo Integration Status</CardTitle>
                <CardDescription>Real-time ERP synchronization results</CardDescription>
              </CardHeader>
              <CardContent>
                {result ? (
                  <div className="space-y-4">
                    {/* Main Status */}
                    <div className={`flex items-center gap-3 p-4 rounded-lg border ${
                      result.status === "Success" 
                        ? "bg-secondary/10 border-secondary/20" 
                        : result.status === "Error"
                        ? "bg-destructive/10 border-destructive/20"
                        : "bg-processing/10 border-processing/20"
                    }`}>
                      {result.status === "Success" ? (
                        <CheckCircle className="w-6 h-6 text-secondary" />
                      ) : (
                        <AlertTriangle className="w-6 h-6 text-destructive" />
                      )}
                      <div>
                        <p className="font-semibold text-foreground">
                          {result.status === "Success" 
                            ? "Successfully Synced to Odoo" 
                            : result.status === "Error"
                            ? "Sync Failed"
                            : "Partial Success"}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {result.error || "Data pushed to ERP system"}
                        </p>
                      </div>
                    </div>

                    {/* Record Details */}
                    <div className="space-y-3">
                      <div className="p-3 rounded-lg bg-muted/50">
                        <p className="text-sm text-muted-foreground mb-1">ERP Record ID</p>
                        <p className="text-lg font-semibold text-foreground font-mono">{result.recordId}</p>
                      </div>
                      
                      <div className="p-3 rounded-lg bg-muted/50">
                        <p className="text-sm text-muted-foreground mb-1">Status</p>
                        <Badge className={getStatusBadgeColor(result.status)}>
                          {result.status}
                        </Badge>
                      </div>

                      {result.odooCustomerId && (
                        <div className="p-3 rounded-lg bg-muted/50">
                          <p className="text-sm text-muted-foreground mb-1">Odoo Customer ID</p>
                          <p className="text-lg font-semibold text-foreground">#{result.odooCustomerId}</p>
                        </div>
                      )}

                      {result.odooLeadId && (
                        <div className="p-3 rounded-lg bg-muted/50">
                          <p className="text-sm text-muted-foreground mb-1">Odoo Sales Lead ID</p>
                          <p className="text-lg font-semibold text-foreground">#{result.odooLeadId}</p>
                        </div>
                      )}

                      <div className="p-3 rounded-lg bg-muted/50">
                        <p className="text-sm text-muted-foreground mb-1">Timestamp</p>
                        <p className="text-sm text-foreground">{new Date(result.timestamp).toLocaleString()}</p>
                      </div>
                    </div>

                    {/* Success Message */}
                    {result.status === "Success" && (
                      <div className="p-4 rounded-lg bg-secondary/10 border border-secondary/20">
                        <p className="text-sm text-secondary font-medium">✅ Data Successfully Created in Odoo:</p>
                        <ul className="text-sm text-muted-foreground mt-2 space-y-1">
                          <li>• Customer record created in Odoo CRM</li>
                          <li>• Sales opportunity generated</li>
                          <li>• Real-time sync completed</li>
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    <Database className="w-16 h-16 mx-auto mb-4 opacity-20" />
                    <p className="text-lg font-medium mb-2">Ready to Sync</p>
                    <p className="text-sm">
                      Enter customer data above to create records in Odoo ERP
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

export default ErpDemo;