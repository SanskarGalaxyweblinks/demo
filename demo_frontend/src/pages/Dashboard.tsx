import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Mail, 
  FileText, 
  Brain, 
  Send, 
  Database,
  CheckCircle2,
  Clock,
  ArrowRight,
  Sparkles,
  Copy,
  Check
} from "lucide-react";

interface WorkflowStep {
  id: string;
  title: string;
  icon: any;
  status: "completed" | "processing" | "pending";
  description: string;
}

const Dashboard = () => {
  const [copied, setCopied] = useState(false);
  const demoEmail = "demoemail@jupiterbrains.com";

  const handleCopy = () => {
    navigator.clipboard.writeText(demoEmail);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const [workflowSteps] = useState<WorkflowStep[]>([
    {
      id: "email",
      title: "Email Received",
      icon: Mail,
      status: "completed",
      description: "New email from client@example.com"
    },
    {
      id: "classify",
      title: "Email Classification",
      icon: Brain,
      status: "processing",
      description: "Analyzing email content and intent"
    },
    {
      id: "extract",
      title: "Document Extraction",
      icon: FileText,
      status: "pending",
      description: "Processing attachments (2 files)"
    },
    {
      id: "response",
      title: "Response Generation",
      icon: Send,
      status: "pending",
      description: "Generating automated response"
    },
    {
      id: "erp",
      title: "ERP Integration",
      icon: Database,
      status: "pending",
      description: "Creating ERP entries"
    }
  ]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="w-5 h-5 text-secondary" />;
      case "processing":
        return <Clock className="w-5 h-5 text-processing animate-spin" />;
      default:
        return <Clock className="w-5 h-5 text-muted-foreground" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      completed: "bg-secondary/10 text-secondary border-secondary/20",
      processing: "bg-processing/10 text-processing border-processing/20",
      pending: "bg-muted text-muted-foreground border-border"
    };
    return variants[status as keyof typeof variants];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">JupiterBrains</h1>
              <p className="text-xs text-muted-foreground">AI Classification Demo</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" asChild>
              <a href={`mailto:${demoEmail}`}>
                <Mail className="w-4 h-4" />
                {demoEmail}
              </a>
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={handleCopy}
              className="h-9 w-9"
            >
              {copied ? (
                <Check className="h-4 w-4 text-secondary" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
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
                  <p className="text-sm text-muted-foreground">Emails Processed</p>
                  <p className="text-2xl font-bold text-foreground">127</p>
                </div>
                <Mail className="w-8 h-8 text-primary/50" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Documents Parsed</p>
                  <p className="text-2xl font-bold text-foreground">243</p>
                </div>
                <FileText className="w-8 h-8 text-primary/50" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Auto Responses</p>
                  <p className="text-2xl font-bold text-foreground">98</p>
                </div>
                <Send className="w-8 h-8 text-secondary/70" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">ERP Entries</p>
                  <p className="text-2xl font-bold text-foreground">76</p>
                </div>
                <Database className="w-8 h-8 text-processing/70" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Workflow Pipeline */}
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-primary" />
              Active Processing Pipeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {workflowSteps.map((step, index) => {
                const Icon = step.icon;
                return (
                  <div key={step.id}>
                    <div className="flex items-start gap-4 p-4 rounded-lg hover:bg-muted/50 transition-colors">
                      <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${
                        step.status === "completed" 
                          ? "bg-secondary/10" 
                          : step.status === "processing" 
                          ? "bg-processing/10" 
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
                          <Badge className={getStatusBadge(step.status)}>
                            {step.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">{step.description}</p>
                      </div>

                      {getStatusIcon(step.status)}
                    </div>
                    
                    {index < workflowSteps.length - 1 && (
                      <div className="flex justify-center py-2">
                        <ArrowRight className="w-5 h-5 text-muted-foreground" />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>Recent Email Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { from: "client@example.com", subject: "Project Requirements Document", time: "2 min ago", status: "processing" },
                { from: "sales@partner.com", subject: "Integration Request", time: "15 min ago", status: "completed" },
                { from: "support@customer.com", subject: "Technical Support Inquiry", time: "1 hour ago", status: "completed" }
              ].map((email, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors">
                  <div className="flex items-center gap-3">
                    <Mail className="w-4 h-4 text-primary" />
                    <div>
                      <p className="font-medium text-sm text-foreground">{email.subject}</p>
                      <p className="text-xs text-muted-foreground">{email.from}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-muted-foreground">{email.time}</span>
                    <Badge className={getStatusBadge(email.status)}>
                      {email.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Dashboard;
