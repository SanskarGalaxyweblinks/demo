import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, Mail, FileText, Shield, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Demo = () => {
  const navigate = useNavigate();

  const models = [
    {
      id: "email",
      icon: Mail,
      name: "KYC Email Classifier",
      description: "Test email classification for onboarding requests, disputes, and general inquiries",
      color: "from-primary to-[hsl(195,100%,45%)]",
      route: "/demo/email"
    },
    {
      id: "document", 
      icon: FileText,
      name: "Document Extractor",
      description: "Extract PII and invoice data from customer documents",
      color: "from-secondary to-[hsl(158,64%,42%)]",
      route: "/demo/document"
    },
    {
      id: "tamper",
      icon: Shield,
      name: "Tamper Detection",
      description: "Identify manipulated or fraudulent documents",
      color: "from-processing to-[hsl(45,93%,47%)]", 
      route: "/demo/tamper"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      <div className="container mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-card/80 backdrop-blur-sm border border-border/50 mb-6">
            <Brain className="w-5 h-5 text-primary" />
            <span className="text-sm font-medium text-foreground">KYC Demo Hub</span>
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Choose a Demo to Test
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Select one of our KYC AI models to experience automated customer onboarding
          </p>
        </div>

        {/* Model Grid */}
        <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto mb-12">
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
                  <CardTitle className="text-xl text-foreground">{model.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">
                    {model.description}
                  </p>
                  <Button 
                    onClick={() => navigate(model.route)}
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

        {/* Navigation */}
        <div className="text-center space-y-4">
          <Button onClick={() => navigate("/models")} variant="outline" size="lg">
            Back to Models Overview
          </Button>
          <div className="text-sm text-muted-foreground">
            Or view the <Button variant="link" onClick={() => navigate("/dashboard")} className="p-0 h-auto">ERP Dashboard</Button> to see processed data
          </div>
        </div>
      </div>
    </div>
  );
};

export default Demo;