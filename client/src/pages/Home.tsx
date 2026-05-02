import { useAuth } from "@/_core/hooks/useAuth";
import { trpc } from "@/lib/trpc";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Loader2, Activity, FileText, Send, GitBranch, AlertCircle } from "lucide-react";
import { getLoginUrl } from "@/const";
import { useState } from "react";

export default function Home() {
  const { user, loading, isAuthenticated } = useAuth();
  const [selectedTask, setSelectedTask] = useState<string | null>(null);

  // Fetch dashboard data
  const tasksQuery = trpc.automation.tasks.useQuery(undefined, { enabled: isAuthenticated });
  const logsQuery = trpc.logs.recent.useQuery(50, { enabled: isAuthenticated });
  const productsQuery = trpc.products.all.useQuery(undefined, { enabled: isAuthenticated });
  const blogsQuery = trpc.blogs.all.useQuery(undefined, { enabled: isAuthenticated });
  const campaignsQuery = trpc.campaigns.all.useQuery(undefined, { enabled: isAuthenticated });

  if (loading) {
    return (
      <div className="min-h-screen bg-background grid-pattern flex items-center justify-center">
        <Loader2 className="animate-spin text-primary w-12 h-12" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-background grid-pattern flex flex-col items-center justify-center">
        <div className="text-center space-y-6">
          <h1 className="text-4xl font-bold text-gradient">Neo Pulse Hub</h1>
          <p className="text-xl text-muted-foreground">AI Automation Dashboard</p>
          <a href={getLoginUrl()}>
            <Button className="bg-primary hover:bg-primary/80 text-primary-foreground">
              Sign In to Dashboard
            </Button>
          </a>
        </div>
      </div>
    );
  }

  // Calculate KPIs
  const totalProducts = productsQuery.data?.length || 0;
  const totalBlogs = blogsQuery.data?.length || 0;
  const totalCampaigns = campaignsQuery.data?.length || 0;
  const successfulTasks = tasksQuery.data?.filter(t => t.status === "success").length || 0;

  // Get task statuses
  const taskStatuses = tasksQuery.data?.reduce((acc, task) => {
    acc[task.name] = task.status;
    return acc;
  }, {} as Record<string, string>) || {};

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "status-success";
      case "error":
        return "status-error";
      case "running":
        return "status-running";
      case "pending":
        return "status-pending";
      default:
        return "status-warning";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "running":
        return <Activity className="w-4 h-4 animate-spin" />;
      case "success":
        return "✓";
      case "error":
        return <AlertCircle className="w-4 h-4" />;
      default:
        return "○";
    }
  };

  return (
    <div className="min-h-screen bg-background grid-pattern">
      {/* Header */}
      <div className="border-b border-border bg-card/50 backdrop-blur">
        <div className="container py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gradient">Neo Pulse Hub</h1>
              <p className="text-sm text-muted-foreground mt-1">AI Automation Dashboard</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Welcome back</p>
              <p className="font-semibold text-foreground">{user?.name || "User"}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container py-8 space-y-8">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="kpi-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Products Fetched</p>
                <p className="text-3xl font-bold text-primary mt-2">{totalProducts}</p>
              </div>
              <Activity className="w-8 h-8 text-primary/50" />
            </div>
            <p className="text-xs text-muted-foreground mt-4">Today's automation cycle</p>
          </div>

          <div className="kpi-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Blog Posts Generated</p>
                <p className="text-3xl font-bold text-secondary mt-2">{totalBlogs}</p>
              </div>
              <FileText className="w-8 h-8 text-secondary/50" />
            </div>
            <p className="text-xs text-muted-foreground mt-4">Content created</p>
          </div>

          <div className="kpi-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Campaigns Sent</p>
                <p className="text-3xl font-bold text-accent mt-2">{totalCampaigns}</p>
              </div>
              <Send className="w-8 h-8 text-accent/50" />
            </div>
            <p className="text-xs text-muted-foreground mt-4">Telegram posts</p>
          </div>

          <div className="kpi-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Successful Tasks</p>
                <p className="text-3xl font-bold text-green-400 mt-2">{successfulTasks}</p>
              </div>
              <GitBranch className="w-8 h-8 text-green-400/50" />
            </div>
            <p className="text-xs text-muted-foreground mt-4">GitHub syncs</p>
          </div>
        </div>

        {/* Task Status Overview */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-foreground">Automation Tasks Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {["fetch-products", "generate-content", "publish-social", "sync-github"].map((taskName) => (
              <div
                key={taskName}
                className="task-card cursor-pointer"
                onClick={() => setSelectedTask(taskName)}
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-foreground capitalize">{taskName.replace("-", " ")}</h3>
                  <Badge className={`${getStatusColor(taskStatuses[taskName] || "pending")} flex items-center gap-1`}>
                    {getStatusIcon(taskStatuses[taskName] || "pending")}
                    {taskStatuses[taskName] || "pending"}
                  </Badge>
                </div>
                <div className="space-y-2 text-xs text-muted-foreground">
                  <p>Last Run: {tasksQuery.data?.find(t => t.name === taskName)?.lastRun ? new Date(tasksQuery.data.find(t => t.name === taskName)!.lastRun!).toLocaleString() : "Never"}</p>
                  <p>Next Run: {tasksQuery.data?.find(t => t.name === taskName)?.nextRun ? new Date(tasksQuery.data.find(t => t.name === taskName)!.nextRun!).toLocaleString() : "Pending"}</p>
                </div>
                  <Button
                  size="sm"
                  className="w-full mt-4 bg-primary/20 hover:bg-primary/40 text-primary border border-primary/50"
                  onClick={(e) => {
                    e.stopPropagation();
                  }}
                >
                  Trigger Now
                </Button>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Logs */}
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-foreground">Recent Execution Logs</h2>
          <Card className="bg-card border-primary/20">
            <div className="divide-y divide-border max-h-96 overflow-y-auto">
              {logsQuery.data && logsQuery.data.length > 0 ? (
                logsQuery.data.slice(0, 10).map((log) => (
                  <div key={log.id} className="p-4 hover:bg-popover/50 transition-colors">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-semibold text-foreground text-sm">{log.taskName}</p>
                      <Badge className={getStatusColor(log.status)}>{log.status}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">{log.message}</p>
                    <p className="text-xs text-muted-foreground/50 mt-1">{new Date(log.timestamp).toLocaleString()}</p>
                  </div>
                ))
              ) : (
                <div className="p-4 text-center text-muted-foreground">No logs yet</div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

