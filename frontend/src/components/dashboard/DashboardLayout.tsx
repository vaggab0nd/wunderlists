import { useState, ReactNode } from "react";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";
import { TopMenuBar } from "@/components/dashboard/TopMenuBar";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";

interface DashboardLayoutProps {
  children: ReactNode;
  maxWidth?: "4xl" | "7xl";
  showHeader?: boolean;
}

export function DashboardLayout({ 
  children, 
  maxWidth = "4xl",
  showHeader = true 
}: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const maxWidthClass = maxWidth === "7xl" ? "max-w-7xl" : "max-w-4xl";

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Top Menu Bar */}
      <div className="fixed top-0 left-0 right-0 z-40">
        <TopMenuBar />
      </div>

      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      {/* Mobile header with menu button */}
      <div className="lg:hidden fixed top-10 left-0 right-0 z-30 bg-background border-b border-border px-4 py-3 flex items-center gap-3">
        <Button 
          variant="ghost" 
          size="icon"
          onClick={() => setSidebarOpen(true)}
        >
          <Menu className="w-5 h-5" />
        </Button>
        <span className="font-semibold text-foreground">Wunderlists</span>
      </div>
      
      <main className="lg:ml-64 transition-all duration-300 mt-10">
        <div className={`${maxWidthClass} mx-auto p-4 lg:p-6 pt-16 lg:pt-6`}>
          {showHeader && <Header />}
          {children}
        </div>
      </main>
    </div>
  );
}
