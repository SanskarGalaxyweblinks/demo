import { Button } from "@/components/ui/button";
import { ArrowLeft, Database, Sparkles } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { ChatInterface } from "@/components/chatbot/ChatInterface";

const ChatbotDemo = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/models">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-accent/10 border border-accent/20">
              <Sparkles className="w-4 h-4 text-accent" />
              <span className="text-sm font-medium text-foreground">JupiterBrains Chat Lens</span>
            </div>
          </div>
          <Button variant="outline" onClick={() => navigate("/dashboard")}>
            <Database className="w-4 h-4 mr-2" />
            ERP Dashboard
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-6 py-6 h-[calc(100vh-80px)]">
        <div className="max-w-4xl mx-auto h-full bg-card/30 border border-border/50 rounded-2xl p-6 backdrop-blur-sm shadow-sm">
           <ChatInterface />
        </div>
      </div>
    </div>
  );
};

export default ChatbotDemo;