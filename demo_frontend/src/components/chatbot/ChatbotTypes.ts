export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  sources?: string[];
  type?: "final" | "intermediate" | "error";
  section?: "Database" | "Vector" | "Web" | "Summary";
  // Add this new field to persist the thinking steps
  thoughts?: {
    database?: string;
    vector?: string;
    web?: string;
  };
}

export interface StreamStatus {
  step: "idle" | "database" | "vector" | "web" | "summary";
  isStreaming: boolean;
}