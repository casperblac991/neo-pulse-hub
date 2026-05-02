import { trpc } from "@/lib/trpc";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Loader2, AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { useMemo } from "react";

export default function Health() {
  const healthQuery = trpc.health.all.useQuery();
  const health = healthQuery.data || [];

  const services = ["openclaw", "openai", "telegram", "amazon"];

  const getServiceStatus = (serviceName: string) => {
    return health.find(h => h.service === serviceName);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "online":
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case "offline":
        return <XCircle className="w-5 h-5 text-red-400" />;
      case "degraded":
        return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      default:
        return <Activity className="w-5 h-5 text-blue-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "status-success";
      case "offline":
        return "status-error";
      case "degraded":
        return "status-warning";
      default:
        return "status-pending";
    }
  };

  const onlineCount = health.filter(h => h.status === "online").length;
  const offlineCount = health.filter(h => h.status === "offline").length;
  const degradedCount = health.filter(h => h.status === "degraded").length;

  return (
    <div className="min-h-screen bg-background grid-pattern">
      {/* Header */}
      <div className="border-b border-border bg-card/50 backdrop-blur">
        <div className="container py-6">
          <h1 className="text-3xl font-bold text-gradient">System Health Monitor</h1>
          <p className="text-sm text-muted-foreground mt-1">Monitor API connectivity and service status</p>
        </div>
      </div>

      {/* Content */}
      <div className="container py-8 space-y-6">
        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="kpi-card">
            <p className="text-sm text-muted-foreground">Services Online</p>
            <p className="text-3xl font-bold text-green-400 mt-2">{onlineCount}</p>
          </div>
          <div className="kpi-card">
            <p className="text-sm text-muted-foreground">Degraded</p>
            <p className="text-3xl font-bold text-yellow-400 mt-2">{degradedCount}</p>
          </div>
          <div className="kpi-card">
            <p className="text-sm text-muted-foreground">Offline</p>
            <p className="text-3xl font-bold text-red-400 mt-2">{offlineCount}</p>
          </div>
        </div>

        {/* Services Grid */}
        {healthQuery.isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="animate-spin text-primary w-8 h-8" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {services.map(serviceName => {
              const serviceHealth = getServiceStatus(serviceName);
              const status = serviceHealth?.status || "unknown";

              return (
                <Card
                  key={serviceName}
                  className="bg-card border-primary/20 hover:border-primary/50 transition-all p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-foreground capitalize text-lg">
                        {serviceName === "openclaw" && "OpenClaw Gateway"}
                        {serviceName === "openai" && "OpenAI API"}
                        {serviceName === "telegram" && "Telegram Bot"}
                        {serviceName === "amazon" && "Amazon API"}
                      </h3>
                      <p className="text-xs text-muted-foreground mt-1">
                        Last checked: {serviceHealth?.lastCheck ? new Date(serviceHealth.lastCheck).toLocaleString() : "Never"}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(status)}
                      <Badge className={getStatusColor(status)}>
                        {status}
                      </Badge>
                    </div>
                  </div>

                  {/* Service Details */}
                  {serviceHealth?.details && (
                    <div className="bg-popover/50 rounded p-3 text-xs text-muted-foreground">
                      <p className="font-mono">{serviceHealth.details}</p>
                    </div>
                  )}

                  {/* Service Description */}
                  <div className="mt-4 text-xs text-muted-foreground space-y-1">
                    {serviceName === "openclaw" && (
                      <>
                        <p>• Manages automation tasks and scheduling</p>
                        <p>• Coordinates all AI-powered workflows</p>
                      </>
                    )}
                    {serviceName === "openai" && (
                      <>
                        <p>• Generates blog content and product descriptions</p>
                        <p>• Powers AI content creation pipeline</p>
                      </>
                    )}
                    {serviceName === "telegram" && (
                      <>
                        <p>• Sends automated marketing campaigns</p>
                        <p>• Broadcasts product updates and promotions</p>
                      </>
                    )}
                    {serviceName === "amazon" && (
                      <>
                        <p>• Fetches product data and pricing</p>
                        <p>• Retrieves affiliate product information</p>
                      </>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        )}

        {/* System Information */}
        <Card className="bg-card border-primary/20 p-6">
          <h3 className="font-semibold text-foreground mb-4">System Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Dashboard Version</p>
              <p className="text-foreground font-mono">1.0.0</p>
            </div>
            <div>
              <p className="text-muted-foreground">Last System Check</p>
              <p className="text-foreground font-mono">{new Date().toLocaleString()}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Automation Engine</p>
              <p className="text-foreground font-mono">OpenClaw v2026.4.27</p>
            </div>
            <div>
              <p className="text-muted-foreground">Database</p>
              <p className="text-foreground font-mono">MySQL/TiDB Connected</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
