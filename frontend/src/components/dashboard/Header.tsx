import { Share2, ArrowUpDown, MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useLocation } from "react-router-dom";

const pageTitles: Record<string, string> = {
  "/": "Inbox",
  "/tasks": "Week",
  "/today": "Today",
  "/starred": "Starred",
  "/assigned": "Assigned to me",
  "/notes": "Notes",
  "/habits": "Habits",
  "/settings": "Settings",
};

export function Header() {
  const location = useLocation();
  const title = pageTitles[location.pathname] || "Week";

  return (
    <header className="flex items-center justify-between py-4 mb-4">
      <h1 className="text-2xl font-semibold text-foreground">{title}</h1>
      
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground">
          <Share2 className="w-4 h-4" />
          <span className="hidden sm:inline">Share</span>
        </Button>
        <Button variant="ghost" size="sm" className="gap-2 text-muted-foreground">
          <ArrowUpDown className="w-4 h-4" />
          <span className="hidden sm:inline">Sort</span>
        </Button>
        <Button variant="ghost" size="icon" className="text-muted-foreground">
          <MoreHorizontal className="w-4 h-4" />
        </Button>
      </div>
    </header>
  );
}