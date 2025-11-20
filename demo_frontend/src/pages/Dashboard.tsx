import { useEffect } from "react";

const Dashboard = () => {
  useEffect(() => {
    // Redirect directly to live Odoo ERP
    window.open("http://3.6.198.245:8089", "_blank");
    // Go back to models page
    window.location.href = "/models";
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-foreground mb-4">Redirecting to Live Odoo ERP...</h1>
        <p className="text-muted-foreground">Opening your real ERP system in a new tab</p>
      </div>
    </div>
  );
};

export default Dashboard;