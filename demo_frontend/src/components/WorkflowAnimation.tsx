import React, { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Mail, 
  FileText, 
  Shield, 
  Database, 
  ArrowRight, 
  CheckCircle2, 
  Loader2,
  Clock,
  BrainCircuit
} from "lucide-react";

interface WorkflowStep {
  id: string;
  title: string;
  icon: any;
  status: "pending" | "processing" | "completed" | "error";
  description: string;
  result?: string;
  processingTime?: number;
}

interface WorkflowAnimationProps {
  steps: WorkflowStep[];
  currentStep?: string;
  progress: number;
  isProcessing: boolean;
}

const WorkflowAnimation: React.FC<WorkflowAnimationProps> = ({
  steps,
  currentStep,
  progress,
  isProcessing
}) => {
  const [animationPhase, setAnimationPhase] = useState<"mailbox" | "processing" | "database" | "complete">("mailbox");

  useEffect(() => {
    if (!isProcessing) {
      setAnimationPhase("mailbox");
      return;
    }

    if (progress === 0) {
      setAnimationPhase("mailbox");
    } else if (progress < 75) {
      setAnimationPhase("processing");
    } else if (progress < 100) {
      setAnimationPhase("database");
    } else {
      setAnimationPhase("complete");
    }
  }, [progress, isProcessing]);

  const getStepIcon = (step: WorkflowStep) => {
    const Icon = step.icon;
    
    if (step.status === "processing") {
      return <Loader2 className="w-5 h-5 animate-spin text-white" />;
    } else if (step.status === "completed") {
      return <CheckCircle2 className="w-5 h-5 text-white" />;
    } else {
      return <Icon className="w-5 h-5 text-muted-foreground" />;
    }
  };

  const getStepBadgeVariant = (status: string) => {
    switch (status) {
      case "completed": return "default";
      case "processing": return "secondary";
      case "error": return "destructive";
      default: return "outline";
    }
  };

  const getStepBackground = (status: string) => {
    switch (status) {
      case "completed": return "bg-secondary";
      case "processing": return "bg-processing";
      case "error": return "bg-destructive";
      default: return "bg-muted";
    }
  };

  return (
    <Card className="border-border/50 bg-card/80 backdrop-blur-sm">
      <CardContent className="pt-6">
        <div className="space-y-6">
          {/* Visual Flow Animation */}
          <div className="relative">
            <div className="flex items-center justify-between mb-8">
              {/* Mailbox */}
              <div className={`flex flex-col items-center transition-all duration-500 ${
                animationPhase === "mailbox" ? "scale-110 opacity-100" : "scale-100 opacity-60"
              }`}>
                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-500 ${
                  animationPhase === "mailbox" ? "bg-primary animate-pulse" : "bg-primary/50"
                }`}>
                  <Mail className="w-8 h-8 text-white" />
                </div>
                <p className="text-xs text-center mt-2 text-muted-foreground">Email Inbox</p>
              </div>

              {/* Flow Arrow 1 */}
              <div className={`flex-1 mx-4 h-0.5 transition-all duration-1000 ${
                progress > 0 ? "bg-primary" : "bg-border"
              }`}>
                <div className={`w-full h-full bg-gradient-to-r from-primary to-transparent transition-all duration-2000 ${
                  animationPhase === "processing" ? "animate-pulse" : ""
                }`} />
              </div>

              {/* AI Processing */}
              <div className={`flex flex-col items-center transition-all duration-500 ${
                animationPhase === "processing" ? "scale-110 opacity-100" : "scale-100 opacity-60"
              }`}>
                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-500 ${
                  animationPhase === "processing" ? "bg-processing animate-pulse" : "bg-processing/50"
                }`}>
                  <BrainCircuit className="w-8 h-8 text-white" />
                </div>
                <p className="text-xs text-center mt-2 text-muted-foreground">AI Models</p>
              </div>

              {/* Flow Arrow 2 */}
              <div className={`flex-1 mx-4 h-0.5 transition-all duration-1000 ${
                progress > 50 ? "bg-primary" : "bg-border"
              }`}>
                <div className={`w-full h-full bg-gradient-to-r from-primary to-transparent transition-all duration-2000 ${
                  animationPhase === "database" ? "animate-pulse" : ""
                }`} />
              </div>

              {/* Database */}
              <div className={`flex flex-col items-center transition-all duration-500 ${
                animationPhase === "database" || animationPhase === "complete" ? "scale-110 opacity-100" : "scale-100 opacity-60"
              }`}>
                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-500 ${
                  animationPhase === "database" ? "bg-secondary animate-pulse" : 
                  animationPhase === "complete" ? "bg-secondary" : "bg-secondary/50"
                }`}>
                  <Database className="w-8 h-8 text-white" />
                </div>
                <p className="text-xs text-center mt-2 text-muted-foreground">ERP Database</p>
              </div>
            </div>

            {/* Progress Bar */}
            {isProcessing && (
              <div className="w-full bg-border rounded-full h-1 mb-6">
                <div 
                  className="bg-gradient-to-r from-primary via-processing to-secondary h-1 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${progress}%` }}
                />
              </div>
            )}
          </div>

          {/* Detailed Steps */}
          <div className="space-y-3">
            <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Processing Pipeline
            </h3>
            
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center gap-4 p-3 rounded-lg bg-muted/20 border border-border/30">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${getStepBackground(step.status)}`}>
                  {getStepIcon(step)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium text-foreground text-sm">{step.title}</h4>
                    <Badge variant={getStepBadgeVariant(step.status)} className="text-xs">
                      {step.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">{step.description}</p>
                  {step.result && (
                    <p className="text-xs text-secondary mt-1">✓ {step.result}</p>
                  )}
                  {step.processingTime && (
                    <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {step.processingTime}s
                    </p>
                  )}
                </div>

                {index < steps.length - 1 && (
                  <ArrowRight className={`w-4 h-4 transition-colors ${
                    step.status === "completed" ? "text-secondary" : "text-muted-foreground"
                  }`} />
                )}
              </div>
            ))}
          </div>

          {/* Processing Status */}
          {isProcessing && currentStep && (
            <div className="mt-4 p-3 rounded-lg bg-processing/10 border border-processing/20">
              <p className="text-sm font-medium text-processing flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                Currently processing: {steps.find(s => s.id === currentStep)?.title}
              </p>
            </div>
          )}

          {/* Completion Status */}
          {!isProcessing && progress === 100 && (
            <div className="mt-4 p-3 rounded-lg bg-secondary/10 border border-secondary/20">
              <p className="text-sm font-medium text-secondary flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" />
                Workflow completed successfully!
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default WorkflowAnimation;