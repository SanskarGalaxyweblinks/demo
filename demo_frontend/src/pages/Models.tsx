// src/pages/Models.tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, Mail, FileText, Shield, ArrowRight, LogOut, Database, Info } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

const Models = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const models = [
    {
      id: "email",
      icon: Mail,
      name: "Complete KYC Workflow",
      description: "End-to-end automation: Email classification, document extraction, tamper detection, and ERP integration in one unified process.",
      color: "from-primary to-[hsl(195,100%,45%)]",
      route: "/demo/email",
      isMain: true
    },
    {
      id: "document", 
      icon: FileText,
      name: "Document Extractor",
      description: "Standalone document processing: Extract PII from ID documents and invoice data from financial documents.",
      color: "from-secondary to-[hsl(158,64%,42%)]",
      route: "/demo/document",
      isMain: false
    },
    {
      id: "tamper",
      icon: Shield,
      name: "Tamper Detection",
      description: "Standalone fraud detection: Analyze documents for manipulation, editing traces, and authenticity verification.",
      color: "from-processing to-[hsl(45,93%,47%)]",
      route: "/demo/tamper",
      isMain: false
    }
  ];

  const handleTryDemo = (route: string) => {
    if (!user) {
      navigate("/auth");
    } else {
      navigate(route);
    }
  };

  const handleSignOut = () => {
    logout();
    navigate("/auth");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      <div className="container mx-auto px-6 py-12">
        {user && (
          <div className="flex justify-end gap-3 mb-4">
            <Button variant="outline" onClick={() => navigate("/instructions")}>
              <Info className="w-4 h-4 mr-2" />
              Instructions
            </Button>
            <Button variant="outline" onClick={() => navigate("/dashboard")}>
              <Database className="w-4 h-4 mr-2" />
              ERP Dashboard
            </Button>
            <Button variant="outline" onClick={handleSignOut}>
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
          </div>
        )}

        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-card/80 backdrop-blur-sm border border-border/50 mb-6">
            <Brain className="w-5 h-5 text-primary" />
            <span className="text-sm font-medium text-foreground">KYC AI Models</span>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            KYC Automation Models
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Experience our specialized AI models for customer onboarding and compliance automation
          </p>
        </div>

        {/* Featured Model */}
        <div className="mb-12">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-foreground mb-2">Featured Demo</h2>
            <p className="text-muted-foreground">Complete end-to-end KYC automation workflow</p>
          </div>
          
          <Card className="group border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-2 max-w-4xl mx-auto border-primary/20">
            <CardHeader className="text-center">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-[hsl(195,100%,45%)] flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform">
                <Mail className="w-10 h-10 text-white" />
              </div>
              <CardTitle className="text-3xl text-foreground">Complete KYC Workflow</CardTitle>
              <CardDescription className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Send a KYC onboarding email with documents and watch the complete automation: 
                email classification → document extraction → tamper detection → ERP integration
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <div className="grid md:grid-cols-4 gap-4 mb-6">
                <div className="p-3 rounded-lg bg-muted/50">
                  <Mail className="w-6 h-6 text-primary mx-auto mb-2" />
                  <p className="text-sm font-medium">Email Analysis</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/50">
                  <FileText className="w-6 h-6 text-secondary mx-auto mb-2" />
                  <p className="text-sm font-medium">Document Extraction</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/50">
                  <Shield className="w-6 h-6 text-processing mx-auto mb-2" />
                  <p className="text-sm font-medium">Tamper Detection</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/50">
                  <Database className="w-6 h-6 text-accent mx-auto mb-2" />
                  <p className="text-sm font-medium">ERP Integration</p>
                </div>
              </div>
              
              <Button 
                onClick={() => handleTryDemo("/demo/email")}
                className="group/btn"
                variant="hero"
                size="lg"
              >
                Try Complete Workflow
                <ArrowRight className="w-5 h-5 ml-2 group-hover/btn:translate-x-1 transition-transform" />
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Individual Models */}
        <div className="mb-8">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-foreground mb-2">Individual Model Demos</h2>
            <p className="text-muted-foreground">Test specific AI models in isolation</p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {models.filter(model => !model.isMain).map((model) => {
              const Icon = model.icon;
              return (
                <Card 
                  key={model.id} 
                  className="group border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
                >
                  <CardHeader>
                    <div className={`w-14 h-14 rounded-lg bg-gradient-to-br ${model.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                      <Icon className="w-7 h-7 text-white" />
                    </div>
                    <CardTitle className="text-xl text-foreground">{model.name}</CardTitle>
                    <CardDescription className="text-muted-foreground">
                      {model.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Button 
                      onClick={() => handleTryDemo(model.route)}
                      className="w-full group/btn"
                      variant="outline"
                    >
                      Try Individual Demo
                      <ArrowRight className="w-4 h-4 ml-2 group-hover/btn:translate-x-1 transition-transform" />
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Info Section */}
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm max-w-4xl mx-auto">
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <div className="w-12 h-12 mx-auto rounded-xl bg-primary/10 flex items-center justify-center">
                <Info className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-bold text-foreground">How It Works</h3>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Our KYC automation demonstrates how AI can streamline customer onboarding by processing emails, 
                extracting document data, detecting fraud, and updating business systems—all in real-time.
              </p>
              <div className="flex justify-center gap-3 mt-6">
                <Button variant="outline" onClick={() => navigate("/instructions")}>
                  View Instructions
                </Button>
                <Button variant="outline" onClick={() => navigate("/dashboard")}>
                  Live Dashboard
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Bottom CTA */}
        {!user && (
          <div className="text-center mt-12">
            <p className="text-muted-foreground mb-4">
              Sign in to unlock full access to all KYC AI models
            </p>
            <Button onClick={() => navigate("/auth")} variant="hero" size="lg">
              Sign In / Sign Up
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Models;