import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Brain, Mail, FileText, Zap, CheckCircle, ArrowRight, Copy, Check } from "lucide-react";
import { Link } from "react-router-dom";
import { useState } from "react";

const Index = () => {
  const [copied, setCopied] = useState(false);
  const demoEmail = "demoemail@jupiterbrains.com";

  const handleCopy = () => {
    navigator.clipboard.writeText(demoEmail);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const features = [
    {
      icon: Mail,
      title: "Email Classification",
      description: "Intelligent categorization of incoming emails using CPU-optimized small language models"
    },
    {
      icon: FileText,
      title: "Document Processing",
      description: "Extract and analyze content from PDFs, DOCX, and images with precision"
    },
    {
      icon: Zap,
      title: "Automated Responses",
      description: "Generate contextual, policy-compliant responses automatically"
    },
    {
      icon: CheckCircle,
      title: "ERP Integration",
      description: "Seamlessly push parsed data into your ERP system"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,hsl(var(--primary)/0.15),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,hsl(var(--secondary)/0.15),transparent_50%)]" />
        
        <div className="container mx-auto px-6 py-20 relative">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-card/80 backdrop-blur-sm border border-border/50">
              <Brain className="w-5 h-5 text-primary" />
              <span className="text-sm font-medium text-foreground">Powered by AI</span>
            </div>

            <h1 className="text-5xl md:text-6xl font-bold text-foreground leading-tight">
              AI-Powered Email & Document{" "}
              <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                Classification
              </span>
            </h1>

            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Experience the future of workflow automation with JupiterBrains' intelligent 
              classification system. Process emails, extract documents, and generate responses instantly.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button asChild variant="hero" size="xl">
                <Link to="/models">
                  Try Interactive Demo
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="xl">
                <Link to="/dashboard">
                  Live Dashboard
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Complete Workflow Automation
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            From email reception to ERP integration, our AI handles every step of the process
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 max-w-5xl mx-auto">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card key={index} className="border-border/50 bg-card/80 backdrop-blur-sm hover:shadow-lg transition-all">
                <CardContent className="pt-6">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center flex-shrink-0">
                      <Icon className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg text-foreground mb-2">
                        {feature.title}
                      </h3>
                      <p className="text-muted-foreground">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Demo Info Section */}
      <section className="container mx-auto px-6 py-20">
        <Card className="border-border/50 bg-card/80 backdrop-blur-sm max-w-3xl mx-auto">
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <Mail className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-foreground">Demo Environment</h3>
              <p className="text-muted-foreground">
                This demonstration showcases real-time email classification, document extraction, 
                and automated response generation. Send an email to see the AI in action.
              </p>
              <div className="pt-4 flex items-center gap-3 justify-center">
                <a 
                  href={`mailto:${demoEmail}`}
                  className="px-4 py-2 rounded-lg bg-muted text-foreground font-mono text-sm hover:bg-muted/80 transition-colors"
                >
                  {demoEmail}
                </a>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handleCopy}
                  className="h-10 w-10"
                >
                  {copied ? (
                    <Check className="h-4 w-4 text-success" />
                  ) : (
                    <Copy className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
};

export default Index;
