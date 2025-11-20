import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Send, Brain, User, Sparkles, Loader2 } from "lucide-react";
import { StreamSection } from "./StreamSection";
import { ChatMessage, StreamStatus } from "./ChatbotTypes";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown"; 
import remarkGfm from "remark-gfm";

// Using the specific IP you provided
const CHATBOT_API = "http://10.178.206.146:8001";

export const ChatInterface = () => {
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [streamStatus, setStreamStatus] = useState<StreamStatus>({ step: "idle", isStreaming: false });
  
  // Temporary state for streaming chunks (for UI display only)
  const [dbContent, setDbContent] = useState("");
  const [vectorContent, setVectorContent] = useState("");
  const [webContent, setWebContent] = useState("");
  const [summaryContent, setSummaryContent] = useState("");
  const [currentSources, setCurrentSources] = useState<string[]>([]);

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [history, dbContent, vectorContent, webContent, summaryContent]);

  const processStream = async (endpoint: string, body: any, onChunk: (text: string) => void, onSources?: (srcs: string[]) => void) => {
    try {
      const response = await fetch(`${CHATBOT_API}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!response.ok) throw new Error("Network response was not ok");
      if (!response.body) return "";

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedText = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n\n");
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const jsonStr = line.replace("data: ", "");
              const data = JSON.parse(jsonStr);
              
              if (data.type === "chunk") {
                accumulatedText += data.data;
                onChunk(accumulatedText);
              } else if (data.type === "sources" && onSources) {
                onSources(data.data);
              }
            } catch (e) {
              // Ignore parse errors for incomplete chunks
            }
          }
        }
      }
      return accumulatedText;
    } catch (error) {
      console.error(`Error streaming from ${endpoint}:`, error);
      return "";
    }
  };

  const handleSend = async () => {
    if (!query.trim() || streamStatus.isStreaming) return;

    const userMsg: ChatMessage = { id: Date.now().toString(), role: "user", content: query };
    setHistory(prev => [...prev, userMsg]);
    setQuery("");
    setStreamStatus({ step: "database", isStreaming: true });
    
    // Reset temporary contents
    setDbContent("");
    setVectorContent("");
    setWebContent("");
    setSummaryContent("");
    setCurrentSources([]);

    const collectedSources: string[] = [];

    try {
      // 1. Database Stream
      const dbResult = await processStream("/stream-db", { query: userMsg.content, language: "English" }, setDbContent);
      
      // 2. Vector Stream
      setStreamStatus(prev => ({ ...prev, step: "vector" }));
      const vectorResult = await processStream(
        "/stream-vector", 
        { query: userMsg.content, language: "English" }, 
        setVectorContent, 
        (srcs) => {
          setCurrentSources(prev => [...prev, ...srcs]);
          collectedSources.push(...srcs);
        }
      );

      // 3. Web Stream
      setStreamStatus(prev => ({ ...prev, step: "web" }));
      const webResult = await processStream(
        "/stream-web", 
        { query: userMsg.content, language: "English" }, 
        setWebContent, 
        (srcs) => {
          setCurrentSources(prev => [...prev, ...srcs]);
          collectedSources.push(...srcs);
        }
      );

      // 4. Summary Stream
      setStreamStatus(prev => ({ ...prev, step: "summary" }));
      const summaryResult = await processStream("/stream-summary", { 
        user_query: userMsg.content,
        db_response: dbResult,
        article_response: vectorResult + "\n" + webResult, 
        language: "English"
      }, setSummaryContent);

      // Finalize
      const finalMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: summaryResult || "I couldn't generate a summary, but please check the data sources above.",
        sources: collectedSources,
        // PERSIST THE THINKING STEPS HERE
        thoughts: {
          database: dbResult,
          vector: vectorResult,
          web: webResult
        }
      };
      
      setHistory(prev => [...prev, finalMsg]);
      setStreamStatus({ step: "idle", isStreaming: false });
      
    } catch (error) {
      toast.error("Failed to process request");
      setStreamStatus({ step: "idle", isStreaming: false });
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)]">
      <ScrollArea className="flex-1 pr-4">
        <div className="space-y-6 pb-4">
          {history.length === 0 && (
             <div className="h-[400px] flex flex-col items-center justify-center text-center text-muted-foreground opacity-50">
               <div className="w-20 h-20 bg-accent/20 rounded-full flex items-center justify-center mb-4">
                 <Sparkles className="w-10 h-10 text-accent" />
               </div>
               <h3 className="font-semibold text-lg">JupiterBrains Chat Lens</h3>
               <p className="text-sm max-w-sm mt-2">Ask about financial data, market trends, or company details. I'll analyze databases, documents, and the web.</p>
             </div>
          )}

          {history.map((msg) => (
            <div key={msg.id} className={cn("flex gap-4", msg.role === "user" ? "justify-end" : "justify-start")}>
              {msg.role !== "user" && (
                <Avatar className="w-8 h-8 border border-border bg-accent/10 flex-shrink-0">
                  <AvatarImage src="/jupiter-logo.png" />
                  <AvatarFallback><Brain className="w-4 h-4 text-accent" /></AvatarFallback>
                </Avatar>
              )}
              
              <div className={cn("max-w-[85%] flex flex-col gap-2", msg.role === "user" ? "items-end" : "items-start")}>
                
                {/* RENDER PERSISTED THINKING COMPONENT */}
                {msg.role === "assistant" && msg.thoughts && (
                  <div className="w-full mb-2 space-y-2">
                    {msg.thoughts.database && (
                      <StreamSection title="Analyzed Structured Database" content={msg.thoughts.database} type="database" status="completed" />
                    )}
                    {msg.thoughts.vector && (
                      <StreamSection title="Retrieved Internal Documents" content={msg.thoughts.vector} type="vector" status="completed" sources={msg.sources} />
                    )}
                    {msg.thoughts.web && (
                      <StreamSection title="Scanned Web Data" content={msg.thoughts.web} type="web" status="completed" />
                    )}
                  </div>
                )}

                <div className={cn(
                  "p-4 rounded-2xl text-sm shadow-sm w-full",
                  msg.role === "user" 
                    ? "bg-primary text-primary-foreground rounded-tr-none" 
                    : "bg-card border border-border rounded-tl-none"
                )}>
                   {/* MARKDOWN RENDERER */}
                   <div className={cn("leading-relaxed prose dark:prose-invert prose-p:leading-relaxed prose-pre:p-0 max-w-none", msg.role === "user" ? "text-primary-foreground" : "text-foreground")}>
                     <ReactMarkdown
                       remarkPlugins={[remarkGfm]}
                       components={{
                         p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                         ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-2 space-y-1" {...props} />,
                         ol: ({node, ...props}) => <ol className="list-decimal pl-5 mb-2 space-y-1" {...props} />,
                         li: ({node, ...props}) => <li className="pl-1" {...props} />,
                         a: ({node, ...props}) => <a className="underline underline-offset-2 font-medium hover:opacity-80" {...props} />,
                         strong: ({node, ...props}) => <strong className="font-bold" {...props} />,
                         h1: ({node, ...props}) => <h1 className="text-lg font-bold mt-4 mb-2" {...props} />,
                         h2: ({node, ...props}) => <h2 className="text-base font-bold mt-3 mb-2" {...props} />,
                         h3: ({node, ...props}) => <h3 className="text-sm font-bold mt-3 mb-1" {...props} />,
                         code: ({node, ...props}) => <code className="bg-muted/50 px-1 py-0.5 rounded font-mono text-xs" {...props} />,
                       }}
                     >
                       {msg.content}
                     </ReactMarkdown>
                   </div>

                   {msg.sources && msg.sources.length > 0 && (
                     <div className="mt-3 pt-3 border-t border-border/50 flex flex-wrap gap-2">
                       {msg.sources.map((src, i) => (
                         <span key={i} className="text-[10px] bg-black/5 dark:bg-white/10 px-2 py-1 rounded-full text-muted-foreground">
                           {src}
                         </span>
                       ))}
                     </div>
                   )}
                </div>
              </div>

              {msg.role === "user" && (
                <Avatar className="w-8 h-8 border border-border bg-background">
                  <AvatarFallback><User className="w-4 h-4 text-muted-foreground" /></AvatarFallback>
                </Avatar>
              )}
            </div>
          ))}

          {/* LIVE Streaming State Visualization (Only appears while generating) */}
          {streamStatus.isStreaming && (
            <div className="flex gap-4">
               <Avatar className="w-8 h-8 border border-border bg-accent/10 flex-shrink-0">
                  <AvatarFallback><Brain className="w-4 h-4 text-accent" /></AvatarFallback>
                </Avatar>
                <div className="flex-1 max-w-[85%] space-y-2">
                  
                  {(streamStatus.step === "database" || dbContent) && (
                    <StreamSection 
                      title="Analyzing Structured Database" 
                      content={dbContent} 
                      type="database" 
                      status={streamStatus.step === "database" ? "streaming" : "completed"} 
                    />
                  )}

                  {(streamStatus.step === "vector" || vectorContent) && (
                    <StreamSection 
                      title="Retrieving Internal Documents" 
                      content={vectorContent} 
                      type="vector" 
                      status={streamStatus.step === "vector" ? "streaming" : (vectorContent ? "completed" : "pending")} 
                      sources={currentSources}
                    />
                  )}

                  {(streamStatus.step === "web" || webContent) && (
                    <StreamSection 
                      title="Scanning Live Web Data" 
                      content={webContent} 
                      type="web" 
                      status={streamStatus.step === "web" ? "streaming" : (webContent ? "completed" : "pending")} 
                    />
                  )}
                  
                  {streamStatus.step === "summary" && (
                    <div className="flex items-center gap-2 text-sm text-muted-foreground animate-pulse">
                      <Brain className="w-4 h-4" />
                      <span>Synthesizing insights...</span>
                      {summaryContent && (
                        <div className="mt-2 text-foreground bg-card p-4 rounded-lg border w-full">
                          <ReactMarkdown 
                             remarkPlugins={[remarkGfm]}
                             components={{
                               p: ({node, ...props}) => <p className="mb-2 last:mb-0" {...props} />,
                               ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-2" {...props} />,
                               li: ({node, ...props}) => <li className="pl-1" {...props} />,
                               strong: ({node, ...props}) => <strong className="font-bold" {...props} />,
                             }}
                          >
                            {summaryContent}
                          </ReactMarkdown>
                        </div>
                      )}
                    </div>
                  )}
                </div>
            </div>
          )}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      <div className="mt-4 relative">
        <Textarea 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
             if(e.key === 'Enter' && !e.shiftKey) {
               e.preventDefault();
               handleSend();
             }
          }}
          placeholder="Ask a financial question..."
          className="min-h-[60px] pr-12 resize-none bg-card/50 backdrop-blur-sm"
        />
        <Button 
          size="icon" 
          className="absolute right-2 bottom-2 h-8 w-8 transition-all hover:scale-105" 
          onClick={handleSend}
          disabled={!query.trim() || streamStatus.isStreaming}
          variant={streamStatus.isStreaming ? "secondary" : "default"}
        >
          {streamStatus.isStreaming ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </Button>
      </div>
    </div>
  );
};