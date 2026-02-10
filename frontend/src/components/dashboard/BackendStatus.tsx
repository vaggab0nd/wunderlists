import { useEffect, useState } from "react";
import { Wifi, WifiOff, Loader2 } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

const RAILWAY_API_URL = "https://passionate-perception-production.up.railway.app/api";

type Status = "checking" | "connected" | "disconnected";

export function BackendStatus() {
  const [status, setStatus] = useState<Status>("checking");
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  const checkHealth = async () => {
    setStatus("checking");
    try {
      const response = await fetch(`${RAILWAY_API_URL}/tasks`, {
        method: "GET",
        signal: AbortSignal.timeout(5000),
      });
      setStatus(response.ok ? "connected" : "disconnected");
    } catch {
      setStatus("disconnected");
    }
    setLastCheck(new Date());
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const statusConfig = {
    checking: {
      icon: <Loader2 className="w-3 h-3 animate-spin" />,
      color: "text-muted-foreground",
      label: "Checking...",
    },
    connected: {
      icon: <Wifi className="w-3 h-3" />,
      color: "text-green-500",
      label: "Backend connected",
    },
    disconnected: {
      icon: <WifiOff className="w-3 h-3" />,
      color: "text-destructive",
      label: "Backend offline",
    },
  };

  const config = statusConfig[status];

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={checkHealth}
            className={`flex items-center gap-1.5 px-2 py-1 rounded-md text-xs ${config.color} hover:bg-accent/50 transition-colors`}
          >
            {config.icon}
            <span className="hidden sm:inline">{status === "connected" ? "Live" : status === "disconnected" ? "Offline" : ""}</span>
          </button>
        </TooltipTrigger>
        <TooltipContent side="bottom">
          <p>{config.label}</p>
          {lastCheck && (
            <p className="text-xs text-muted-foreground">
              Last checked: {lastCheck.toLocaleTimeString()}
            </p>
          )}
          <p className="text-xs text-muted-foreground">Click to refresh</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
