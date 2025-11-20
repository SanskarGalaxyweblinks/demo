import { useState } from "react";
import { ChevronDown, ChevronRight, Database, Globe, FileText, CheckCircle2, Loader2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StreamSectionProps {
  title: string;
  content: string;
  type: "database" | "vector" | "web";
  status: "pending" | "streaming" | "completed";
  sources?: string[];
}

export const StreamSection = ({ title, content, type, status, sources }: StreamSectionProps) => {
  const [isExpanded, setIsExpanded] = useState(false);

  // Auto-expand while streaming, collapse on complete
  React.useEffect(() => {
    if (status === "streaming") setIsExpanded(true);
    if (status === "completed") setIsExpanded(false);
  }, [status]);

  const getIcon = () => {
    switch (type) {
      case "database": return <Database className="w-4 h-4" />;
      case "vector": return <FileText className="w-4 h-4" />;
      case "web": return <Globe className="w-4 h-4" />;
    }
  };

  return (
    <div className="mb-3">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={cn(
          "flex items-center gap-2 w-full text-xs font-medium px-3 py-2 rounded-md transition-colors border",
          status === "streaming" ? "bg-primary/10 border-primary/20 text-primary" : 
          status === "completed" ? "bg-muted/50 border-border text-muted-foreground hover:bg-muted" :
          "bg-muted/20 border-transparent text-muted-foreground/50"
        )}
      >
        {status === "streaming" ? <Loader2 className="w-3 h-3 animate-spin" /> : 
         status === "completed" ? <CheckCircle2 className="w-3 h-3" /> : 
         <div className="w-3 h-3" />}
        
        {getIcon()}
        <span>{title}</span>
        
        <div className="ml-auto">
          {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
        </div>
      </button>

      {isExpanded && content && (
        <div className="mt-2 pl-2 border-l-2 border-border ml-2 animate-in slide-in-from-top-2 duration-200">
          <Card className="p-3 bg-card/50 text-xs font-mono text-muted-foreground whitespace-pre-wrap shadow-none">
            {content}
          </Card>
          {sources && sources.length > 0 && (
             <div className="mt-2 flex flex-wrap gap-1">
               {sources.map((src, i) => (
                 <span key={i} className="px-1.5 py-0.5 rounded-sm bg-muted text-[10px] text-muted-foreground border border-border">
                   {src}
                 </span>
               ))}
             </div>
          )}
        </div>
      )}
    </div>
  );
};
import React from 'react';