import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import Landing from "./pages/Landing";
import Products from "./pages/Products";
import Blogs from "./pages/Blogs";
import Campaigns from "./pages/Campaigns";
import Health from "@/pages/Health";
import Copilot from "@/pages/Copilot";
import Videos from "@/pages/Videos";
import AffiliatePrograms from "@/pages/AffiliatePrograms";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Landing} />
      <Route path="/dashboard" component={Home} />
      <Route path="/products" component={Products} />
      <Route path="/blogs" component={Blogs} />
      <Route path="/videos" component={Videos} />
      <Route path="/affiliate-programs" component={AffiliatePrograms} />
      <Route path="/campaigns" component={Campaigns} />
      <Route path="/health" component={Health} />
      <Route path="/copilot" component={Copilot} />
      <Route path="/404" component={NotFound} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider
        defaultTheme="light"
        // switchable
      >
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
