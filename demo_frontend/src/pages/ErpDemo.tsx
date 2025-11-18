import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Database, ArrowLeft, Sparkles, CheckCircle } from "lucide-react";
import { Link } from "react-router-dom";
import { useToast } from "@/hooks/use-toast";

const ErpDemo = () => {
  const [customerName, setCustomerName] = useState("");
  const [orderAmount, setOrderAmount] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleIntegrate = async () => {
    if (!customerName || !orderAmount) {
      toast({
        title: "Missing Information",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    // Simulate ERP integration
    setTimeout(() => {
      setResult({
        recordId: `ERP-${Math.random().toString(36).substr(2, 9).toUpperCase()}`,
        status: "Success",
        timestamp: new Date().toISOString(),
        synced: true
      });
      setLoading(false);
      toast({
        title: "Integration Complete",
        description: "Data has been synced to ERP system",
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
            <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-accent to-[hsl(30,92%,55%)] flex items-center justify-center">
              <Database className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-foreground">ERP Integration Demo</h1>
              <p className="text-muted-foreground">Seamless data synchronization with ERP systems</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Input Section */}
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Input Data</CardTitle>
                <CardDescription>Enter information to sync with ERP</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">Customer Name</label>
                  <Input
                    placeholder="Enter customer name..."
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-foreground mb-2 block">Order Amount</label>
                  <Input
                    type="number"
                    placeholder="Enter order amount..."
                    value={orderAmount}
                    onChange={(e) => setOrderAmount(e.target.value)}
                  />
                </div>
                <Button onClick={handleIntegrate} disabled={loading} className="w-full" variant="default">
                  {loading ? "Syncing..." : "Sync to ERP"}
                  <Sparkles className="w-4 h-4" />
                </Button>
              </CardContent>
            </Card>

            {/* Results Section */}
            <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Integration Status</CardTitle>
                <CardDescription>ERP synchronization results</CardDescription>
              </CardHeader>
              <CardContent>
                {result ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 p-4 rounded-lg bg-secondary/10 border border-secondary/20">
                      <CheckCircle className="w-6 h-6 text-secondary" />
                      <div>
                        <p className="font-semibold text-foreground">Successfully Synced</p>
                        <p className="text-sm text-muted-foreground">Data pushed to ERP system</p>
                      </div>
                    </div>
                    <div className="p-4 rounded-lg bg-muted/50">
                      <p className="text-sm text-muted-foreground mb-1">ERP Record ID</p>
                      <p className="text-lg font-semibold text-foreground font-mono">{result.recordId}</p>
                    </div>
                    <div className="p-4 rounded-lg bg-muted/50">
                      <p className="text-sm text-muted-foreground mb-1">Sync Status</p>
                      <p className="text-lg font-semibold text-secondary">{result.status}</p>
                    </div>
                    <div className="p-4 rounded-lg bg-muted/50">
                      <p className="text-sm text-muted-foreground mb-1">Timestamp</p>
                      <p className="text-sm text-foreground">{new Date(result.timestamp).toLocaleString()}</p>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    Sync data to see ERP integration results
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
