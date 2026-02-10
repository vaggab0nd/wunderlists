import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: "default" | "primary" | "accent";
  trend?: {
    value: number;
    positive: boolean;
  };
}

export function StatCard({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  variant = "default",
  trend 
}: StatCardProps) {
  return (
    <div className={cn(
      "glass-card rounded-xl p-6 hover-lift group",
      variant === "primary" && "border-primary/20",
      variant === "accent" && "border-accent/20"
    )}>
      <div className="flex items-start justify-between">
        <div className="space-y-3">
          <p className="section-title">{title}</p>
          <p className={cn(
            "stat-value",
            variant === "primary" && "text-primary",
            variant === "accent" && "text-accent"
          )}>
            {value}
          </p>
          {subtitle && (
            <p className="text-sm text-muted-foreground">{subtitle}</p>
          )}
          {trend && (
            <div className={cn(
              "inline-flex items-center gap-1 text-sm font-medium",
              trend.positive ? "text-accent" : "text-destructive"
            )}>
              <span>{trend.positive ? "+" : ""}{trend.value}%</span>
              <span className="text-muted-foreground">vs last week</span>
            </div>
          )}
        </div>
        <div className={cn(
          "p-3 rounded-xl transition-all duration-300",
          variant === "default" && "bg-secondary group-hover:bg-secondary/80",
          variant === "primary" && "bg-primary/10 group-hover:bg-primary/20",
          variant === "accent" && "bg-accent/10 group-hover:bg-accent/20"
        )}>
          <Icon className={cn(
            "w-6 h-6",
            variant === "default" && "text-muted-foreground",
            variant === "primary" && "text-primary",
            variant === "accent" && "text-accent"
          )} />
        </div>
      </div>
    </div>
  );
}
