import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  User, 
  FileText, 
  Brain, 
  Shield, 
  Database,
  CheckCircle2,
  Clock,
  ArrowLeft,
  Trash2,
  Eye,
  Calendar
} from "lucide-react";
import { useNavigate } from "react-router-dom";

interface CustomerRecord {
  id: string;
  name: string;
  email: string;
  status: "onboarded" | "pending" | "rejected";
  documentType: string;
  submissionDate: string;
  verificationStatus: "verified" | "flagged" | "pending";
}

const Dashboard = () => {
  const navigate = useNavigate();
  
  const [customerRecords] = useState<CustomerRecord[]>([
    {
      id: "KYC001",
      name: "John Smith",
      email: "john.smith@email.com",
      status: "onboarded",
      documentType: "Driver License + Invoice",
      submissionDate: "2024-11-19",
      verificationStatus: "verified"
    },
    {
      id: "KYC002", 
      name: "Sarah Johnson",
      email: "sarah.j@company.com",
      status: "pending",
      documentType: "Passport + Bank Statement",
      submissionDate: "2024-11-19",
      verificationStatus: "pending"
    },
    {
      id: "KYC003",
      name: "Mike Chen",
      email: "mike.chen@business.com", 
      status: "rejected",
      documentType: "ID Card + Invoice",
      submissionDate: "2024-11-18",
      verificationStatus: "flagged"
    },
    {
      id: "KYC004",
      name: "Emma Davis",
      email: "emma.davis@startup.com",
      status: "onboarded", 
      documentType: "Passport + Utility Bill",
      submissionDate: "2024-11-18",
      verificationStatus: "verified"
    }
  ]);

  const getStatusBadge = (status: string) => {
    const variants = {
      onboarded: "bg-secondary/10 text-secondary border-secondary/20",
      pending: "bg-processing/10 text-processing border-processing/20", 
      rejected: "bg-destructive/10 text-destructive border-destructive/20"
    };
    return variants[status as keyof typeof variants];
  };

  const getVerificationBadge = (status: string) => {
    const variants = {
      verified: "bg-secondary/10 text-secondary border-secondary/20",
      pending: "bg-processing/10 text-processing border-processing/20",
      flagged: "bg-destructive/10 text-destructive border-destructive/20"
    };
    return variants[status as keyof typeof variants];
  };

  const handleDeleteRecord = (id: string) => {
    // Handle record deletion
    console.log("Deleting record:", id);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button variant="ghost" onClick={() => navigate("/models")}>
              <ArrowLeft className="w-4 h-4" />
              Back to Models
            </Button>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Database className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">ERP Dashboard</h1>
              <p className="text-xs text-muted-foreground">Customer Onboarding Records</p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Records</p>
                  <p className="text-2xl font-bold text-foreground">{customerRecords.length}</p>
                </div>
                <User className="w-8 h-8 text-primary/50" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Onboarded</p>
                  <p className="text-2xl font-bold text-foreground">
                    {customerRecords.filter(r => r.status === "onboarded").length}
                  </p>
                </div>
                <CheckCircle2 className="w-8 h-8 text-secondary/70" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Pending Review</p>
                  <p className="text-2xl font-bold text-foreground">
                    {customerRecords.filter(r => r.status === "pending").length}
                  </p>
                </div>
                <Clock className="w-8 h-8 text-processing/70" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Flagged/Rejected</p>
                  <p className="text-2xl font-bold text-foreground">
                    {customerRecords.filter(r => r.status === "rejected").length}
                  </p>
                </div>
                <Shield className="w-8 h-8 text-destructive/70" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Customer Records Table */}
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5 text-primary" />
              Customer Onboarding Records
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {customerRecords.map((record) => (
                <div key={record.id} className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center">
                      <User className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium text-foreground">{record.name}</p>
                        <Badge className={getStatusBadge(record.status)}>
                          {record.status}
                        </Badge>
                        <Badge className={getVerificationBadge(record.verificationStatus)}>
                          {record.verificationStatus}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{record.email}</p>
                      <div className="flex items-center gap-4 mt-1">
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <FileText className="w-3 h-3" />
                          {record.documentType}
                        </span>
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {record.submissionDate}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground font-mono">{record.id}</span>
                    <Button variant="outline" size="icon" className="h-8 w-8">
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="icon" 
                      className="h-8 w-8 text-destructive hover:text-destructive"
                      onClick={() => handleDeleteRecord(record.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* AI Processing Summary */}
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-primary" />
              AI Processing Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 rounded-lg bg-muted/30">
                <div className="w-12 h-12 mx-auto rounded-xl bg-gradient-to-br from-primary to-[hsl(195,100%,45%)] flex items-center justify-center mb-3">
                  <Brain className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-foreground mb-1">Email Classification</h3>
                <p className="text-sm text-muted-foreground">Onboarding: 78% | Disputes: 15% | Other: 7%</p>
              </div>
              
              <div className="text-center p-4 rounded-lg bg-muted/30">
                <div className="w-12 h-12 mx-auto rounded-xl bg-gradient-to-br from-secondary to-[hsl(158,64%,42%)] flex items-center justify-center mb-3">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-foreground mb-1">Document Extraction</h3>
                <p className="text-sm text-muted-foreground">Success Rate: 94% | PII Extracted: 342 fields</p>
              </div>
              
              <div className="text-center p-4 rounded-lg bg-muted/30">
                <div className="w-12 h-12 mx-auto rounded-xl bg-gradient-to-br from-processing to-[hsl(45,93%,47%)] flex items-center justify-center mb-3">
                  <Shield className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-semibold text-foreground mb-1">Tamper Detection</h3>
                <p className="text-sm text-muted-foreground">Documents Flagged: 3 | Confidence: 99.2%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Dashboard;