import { trpc } from "@/lib/trpc";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Send, Loader2, AlertCircle, CheckCircle } from "lucide-react";
import { useMemo } from "react";

export default function Campaigns() {
  const campaignsQuery = trpc.campaigns.all.useQuery();
  const campaigns = campaignsQuery.data || [];

  const stats = useMemo(() => {
    return {
      total: campaigns.length,
      delivered: campaigns.filter(c => c.deliveryStatus === "delivered").length,
      failed: campaigns.filter(c => c.deliveryStatus === "failed").length,
      pending: campaigns.filter(c => c.deliveryStatus === "pending").length,
    };
  }, [campaigns]);

  const getDeliveryIcon = (status: string) => {
    switch (status) {
      case "delivered":
        return <CheckCircle className="w-4 h-4 text-green-400" />;
      case "failed":
        return <AlertCircle className="w-4 h-4 text-red-400" />;
      default:
        return <Send className="w-4 h-4 text-blue-400" />;
    }
  };

  const getDeliveryColor = (status: string) => {
    switch (status) {
      case "delivered":
        return "status-success";
      case "failed":
        return "status-error";
      default:
        return "status-pending";
    }
  };

  return (
    <div className="min-h-screen bg-background grid-pattern">
      {/* Header */}
      <div className="border-b border-border bg-card/50 backdrop-blur">
        <div className="container py-6">
          <h1 className="text-3xl font-bold text-gradient">Telegram Campaigns</h1>
          <p className="text-sm text-muted-foreground mt-1">Track all sent campaigns and delivery status</p>
        </div>
      </div>

      {/* Content */}
      <div className="container py-8 space-y-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="kpi-card">
            <p className="text-sm text-muted-foreground">Total Campaigns</p>
            <p className="text-3xl font-bold text-primary mt-2">{stats.total}</p>
          </div>
          <div className="kpi-card">
            <p className="text-sm text-muted-foreground">Delivered</p>
            <p className="text-3xl font-bold text-green-400 mt-2">{stats.delivered}</p>
          </div>
          <div className="kpi-card">
            <p className="text-sm text-muted-foreground">Pending</p>
            <p className="text-3xl font-bold text-blue-400 mt-2">{stats.pending}</p>
          </div>
          <div className="kpi-card">
            <p className="text-sm text-muted-foreground">Failed</p>
            <p className="text-3xl font-bold text-red-400 mt-2">{stats.failed}</p>
          </div>
        </div>

        {/* Campaigns List */}
        {campaignsQuery.isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="animate-spin text-primary w-8 h-8" />
          </div>
        ) : campaigns.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No campaigns sent yet</p>
          </div>
        ) : (
          <div className="space-y-4">
            {campaigns.map(campaign => (
              <Card
                key={campaign.id}
                className="bg-card border-primary/20 hover:border-primary/50 transition-all p-4"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Send className="w-4 h-4 text-primary" />
                      <p className="font-semibold text-foreground">Campaign {campaign.id.substring(0, 8)}</p>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
                      {campaign.message}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <Badge className={getDeliveryColor(campaign.deliveryStatus)}>
                        <span className="flex items-center gap-1">
                          {getDeliveryIcon(campaign.deliveryStatus)}
                          {campaign.deliveryStatus}
                        </span>
                      </Badge>
                      {campaign.status && (
                        <Badge className="bg-primary/20 text-primary border-primary/30">
                          {campaign.status}
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-muted-foreground">
                      {new Date(campaign.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
                {campaign.error && (
                  <div className="mt-3 p-2 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400">
                    Error: {campaign.error}
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
