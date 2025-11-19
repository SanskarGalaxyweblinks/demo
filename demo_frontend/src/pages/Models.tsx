// src/pages/Models.tsx
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, Mail, FileText, Shield, ArrowRight, LogOut, Database } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

const Models = () => {
  const navigate = useNavigate();
  // UPDATED: Import logout instead of signOut
  const { user, logout } = useAuth();

  const models = [
    {
      id: "email",
      icon: Mail,
      name: "KYC Email Classifier",
      description: "Automatically classify onboarding requests, disputes, and general inquiries from customer emails.",
      color: "from-primary to-[hsl(195,100%,45%)]",
      route: "/demo/email"
    },
    {
      id: "document",
      icon: FileText,
      name: "Document Extractor",
      description: "Extract critical PII, invoice data, and identity information from customer documents with precision.",
      color: "from-secondary to-[hsl(158,64%,42%)]",
      route: "/demo/document"
    },
    {
      id: "tamper",
      icon: Shield,
      name: "Tamper Detection",
      description: "Identify manipulated, edited, or fraudulent documents to ensure compliance and authenticity.",
      color: "from-processing to-[hsl(45,93%,47%)]",
      route: "/demo/tamper"
    }
  ];

  const handleTryDemo = (route: string) => {
    if (!user) {
      navigate("/auth");
    } else {
      navigate(route);
    }
  };

  // Updated logout logic
  const handleSignOut = () => {
    logout();
    navigate("/auth");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      <div className="container mx-auto px-6 py-12">
        {user && (
          <div className="flex justify-end gap-3 mb-4">
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

        {/* Model Grid */}
        <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {models.map((model) => {
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
                  <CardTitle className="text-2xl text-foreground">{model.name}</CardTitle>
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
                    Try Demo
                    <ArrowRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

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