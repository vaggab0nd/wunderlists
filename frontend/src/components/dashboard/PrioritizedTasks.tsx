import { Check, Star, Loader2, User as UserIcon, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";
import { usePrioritizedTasks, useUpdateTask, Task } from "@/hooks/useRailwayData";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

const priorityColors = {
  high: "destructive",
  medium: "default",
  low: "secondary",
} as const;

export function PrioritizedTasks() {
  const { data: tasks = [], isLoading, error } = usePrioritizedTasks();
  const updateTask = useUpdateTask();

  const toggleTask = (task: Task) => {
    updateTask.mutate({ id: task.id, completed: !task.completed });
  };

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map(n => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-4 py-8 text-center">
        <p className="text-sm text-muted-foreground">
          Unable to load prioritized tasks. Please check your backend connection.
        </p>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="px-4 py-8 text-center">
        <TrendingUp className="w-12 h-12 mx-auto mb-3 text-muted-foreground/50" />
        <p className="text-sm text-muted-foreground">
          No prioritized tasks at the moment. Great job staying on top of things!
        </p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-border">
      {tasks.map((task) => (
        <div
          key={task.id}
          className={cn(
            "flex items-center gap-3 px-4 py-3 task-item cursor-pointer hover:bg-muted/50 transition-colors",
            task.completed && "bg-muted/30"
          )}
          onClick={() => toggleTask(task)}
        >
          {/* Checkbox */}
          <button
            className={cn(
              "task-checkbox",
              task.completed && "checked"
            )}
            disabled={updateTask.isPending}
          >
            {task.completed && (
              <Check className="w-3 h-3 text-accent-foreground" />
            )}
          </button>

          {/* Task Content */}
          <div className="flex-1 min-w-0">
            <span className={cn(
              "text-sm",
              task.completed && "line-through text-muted-foreground"
            )}>
              {task.title}
            </span>
            {task.due_date && (
              <p className="text-xs text-muted-foreground mt-1">
                Due: {task.due_date}
              </p>
            )}
          </div>

          {/* Priority Badge */}
          {task.priority && (
            <Badge variant={priorityColors[task.priority]} className="text-xs">
              {task.priority}
            </Badge>
          )}

          {/* Assignee Avatar */}
          {task.assigned_user ? (
            <Avatar className="w-6 h-6">
              <AvatarFallback className="bg-primary/20 text-primary text-xs">
                {getInitials(task.assigned_user.name)}
              </AvatarFallback>
            </Avatar>
          ) : (
            <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center">
              <UserIcon className="w-3 h-3 text-muted-foreground" />
            </div>
          )}

          {/* Star Indicator for High Priority */}
          {task.priority === "high" && (
            <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
          )}
        </div>
      ))}
    </div>
  );
}
