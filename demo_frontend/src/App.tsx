import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import Index from "./pages/Index";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import Demo from "./pages/Demo";
import Models from "./pages/Models";
import EmailDemo from "./pages/EmailDemo";
import DocumentDemo from "./pages/DocumentDemo";
import TamperDetection from "./pages/TamperDetection";
import Instructions from "./pages/Instructions";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/auth" element={<Auth />} />
            <Route path="/models" element={<Models />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/demo" element={<Demo />} />
            <Route path="/instructions" element={<Instructions />} />
            <Route
              path="/demo/email"
              element={
                <ProtectedRoute>
                  <EmailDemo />
                </ProtectedRoute>
              }
            />
            <Route
              path="/demo/document"
              element={
                <ProtectedRoute>
                  <DocumentDemo />
                </ProtectedRoute>
              }
            />
            <Route
              path="/demo/tamper"
              element={
                <ProtectedRoute>
                  <TamperDetection />
                </ProtectedRoute>
              }
            />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </AuthProvider>
  </QueryClientProvider>
);

export default App;