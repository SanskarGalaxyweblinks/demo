import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Mail, 
  FileText, 
  Shield, 
  Database, 
  ArrowRight, 
  CheckCircle, 
  AlertTriangle,
  Info,
  Clock,
  Users,
  Copy,
  Check,
  ArrowLeft
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

const Instructions = () => {
  const navigate = useNavigate();
  const [copied, setCopied] = useState(false);
  const demoEmail = "kyc@jupiterbrains.com";

  const handleCopy = () => {
    navigator.clipboard.writeText(demoEmail);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const workflowSteps = [
    {
      step: 1,
      title: "Customer Email Intake",
      icon: Mail,
      description: "Customer sends onboarding request with documents",
      details: [
        "Customer emails kyc@jupiterbrains.com",
        "Attachments include ID documents and invoices",
        "AI automatically reads and classifies the email intent"
      ],
      categories: ["Onboarding", "Dispute", "Other"]
    },
    {
      step: 2,
      title: "Document Processing",
      icon: FileText,
      description: "Extract critical information from attachments",
      details: [
        "PII extraction from ID documents (name, DOB, address)",
        "Invoice data extraction (amounts, companies, dates)",
        "Automated data validation and formatting"
      ],
      categories: ["PII Data", "Financial Data", "Identity Info"]
    },
    {
      step: 3,
      title: "Tamper Detection",
      icon: Shield,
      description: "Verify document authenticity and detect fraud",
      details: [
        "Metadata analysis for file manipulation signs",
        "Pixel-level analysis for image editing traces",
        "Risk assessment and confidence scoring"
      ],
      categories: ["Authentic", "Flagged", "Manual Review"]
    },
    {
      step: 4,
      title: "ERP Integration",
      icon: Database,
      description: "Automatically update customer records",
      details: [
        "Create new customer record in ERP system",
        "Update onboarding status and verification flags",
        "Generate automated confirmation email to customer"
      ],
      categories: ["Record Created", "Status Updated", "Email Sent"]
    }
  ];

  const sampleEmails = [
    {
      type: "Onboarding Request",
      subject: "New Customer Application - John Smith",
      body: "Hello, I would like to open a new account and complete the KYC process. I have attached my driver's license and bank statement. Please let me know what other documents you need.",
      attachments: ["drivers_license.jpg", "bank_statement.pdf"],
      expectedResult: "Classified as Onboarding | High Priority | PII Extracted"
    },
    {
      type: "Dispute Email",
      subject: "Account Verification Dispute - Case #12345",
      body: "I'm writing to dispute the rejection of my account verification. The documents I submitted are legitimate and I believe there was an error in the review process. Please reconsider my application.",
      attachments: ["passport.pdf"],
      expectedResult: "Classified as Dispute | High Priority | Manual Review"
    },
    {
      type: "General Inquiry",
      subject: "Question about KYC requirements",
      body: "Can you please provide more information about what documents are required for account verification? I want to make sure I submit everything correctly.",
      attachments: [],
      expectedResult: "Classified as Other | Low Priority | No Processing Needed"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Header */}
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
        <div className="max-w-6xl mx-auto">
          {/* Page Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-card/80 backdrop-blur-sm border border-border/50 mb-6">
              <Info className="w-5 h-5 text-primary" />
              <span className="text-sm font-medium text-foreground">Complete Workflow Guide</span>
            </div>
            
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              KYC Automation Instructions
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Learn how our AI-powered system automates the complete customer onboarding process 
              from email intake to ERP integration.
            </p>
          </div>

          {/* Demo Email Section */}
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm mb-12">
            <CardContent className="pt-6">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                  <Mail className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-foreground">Try the Demo</h3>
                <p className="text-muted-foreground">
                  Send an email with documents to see the complete KYC automation in action
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
                      <Check className="h-4 w-4 text-secondary" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Workflow Steps */}
          <div className="mb-12">
            <h2 className="text-3xl font-bold text-foreground mb-8 text-center">
              Complete Automation Workflow
            </h2>
            <div className="space-y-8">
              {workflowSteps.map((step, index) => {
                const Icon = step.icon;
                return (
                  <div key={step.step}>
                    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
                      <CardContent className="pt-6">
                        <div className="flex items-start gap-6">
                          {/* Step Number and Icon */}
                          <div className="flex flex-col items-center">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-white font-bold text-lg mb-2">
                              {step.step}
                            </div>
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary/10 to-secondary/10 flex items-center justify-center">
                              <Icon className="w-8 h-8 text-primary" />
                            </div>
                          </div>

                          {/* Content */}
                          <div className="flex-1">
                            <h3 className="text-2xl font-bold text-foreground mb-2">{step.title}</h3>
                            <p className="text-muted-foreground mb-4">{step.description}</p>
                            
                            <ul className="space-y-2 mb-4">
                              {step.details.map((detail, idx) => (
                                <li key={idx} className="flex items-center gap-2 text-sm">
                                  <CheckCircle className="w-4 h-4 text-secondary flex-shrink-0" />
                                  {detail}
                                </li>
                              ))}
                            </ul>

                            <div className="flex flex-wrap gap-2">
                              {step.categories.map((category, idx) => (
                                <Badge key={idx} variant="outline" className="text-xs">
                                  {category}
                                </Badge>
                              ))}
                            </div>
                          </div>

                          {/* Try Button */}
                          <div className="text-center">
                            <Button 
                              onClick={() => {
                                const routes = ["/demo/email", "/demo/document", "/demo/tamper", "/dashboard"];
                                navigate(routes[index]);
                              }}
                              variant="outline"
                              className="mb-2"
                            >
                              Try This Step
                              <ArrowRight className="w-4 h-4 ml-2" />
                            </Button>
                            <p className="text-xs text-muted-foreground">Interactive Demo</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Connector Arrow */}
                    {index < workflowSteps.length - 1 && (
                      <div className="flex justify-center py-4">
                        <ArrowRight className="w-6 h-6 text-primary" />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Sample Emails Section */}
          <div className="mb-12">
            <h2 className="text-3xl font-bold text-foreground mb-8 text-center">
              Sample Email Scenarios
            </h2>
            <div className="grid md:grid-cols-3 gap-6">
              {sampleEmails.map((email, index) => (
                <Card key={index} className="border-border/50 bg-card/80 backdrop-blur-sm">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Mail className="w-5 h-5 text-primary" />
                      {email.type}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground mb-1">Subject:</p>
                      <p className="text-sm text-foreground">{email.subject}</p>
                    </div>
                    
                    <div>
                      <p className="text-sm font-medium text-muted-foreground mb-1">Body:</p>
                      <p className="text-xs text-muted-foreground italic leading-relaxed">{email.body}</p>
                    </div>

                    {email.attachments.length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-muted-foreground mb-2">Attachments:</p>
                        <div className="space-y-1">
                          {email.attachments.map((attachment, idx) => (
                            <div key={idx} className="flex items-center gap-2 text-xs">
                              <FileText className="w-3 h-3 text-primary" />
                              {attachment}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="p-3 rounded-lg bg-secondary/10 border border-secondary/20">
                      <p className="text-sm font-medium text-muted-foreground mb-1">Expected Result:</p>
                      <p className="text-xs text-secondary">{email.expectedResult}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Key Benefits Section */}
          <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-2xl text-center">Key Benefits of AI-Powered KYC</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center space-y-2">
                  <Clock className="w-10 h-10 mx-auto text-primary" />
                  <h3 className="font-semibold text-foreground">95% Faster</h3>
                  <p className="text-sm text-muted-foreground">Automated processing vs manual review</p>
                </div>
                <div className="text-center space-y-2">
                  <CheckCircle className="w-10 h-10 mx-auto text-secondary" />
                  <h3 className="font-semibold text-foreground">99.2% Accuracy</h3>
                  <p className="text-sm text-muted-foreground">AI-powered classification and extraction</p>
                </div>
                <div className="text-center space-y-2">
                  <Shield className="w-10 h-10 mx-auto text-processing" />
                  <h3 className="font-semibold text-foreground">Fraud Detection</h3>
                  <p className="text-sm text-muted-foreground">Advanced tamper detection algorithms</p>
                </div>
                <div className="text-center space-y-2">
                  <Users className="w-10 h-10 mx-auto text-accent" />
                  <h3 className="font-semibold text-foreground">24/7 Processing</h3>
                  <p className="text-sm text-muted-foreground">Continuous automated onboarding</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Instructions;