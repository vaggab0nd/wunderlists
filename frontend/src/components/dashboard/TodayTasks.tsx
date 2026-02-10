import { Check, User as UserIcon, Calendar, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useDueTodayTasks, useUpdateTask, Task } from "@/hooks/useRailwayData";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

const priorityColors = {
  high: "destructive",
  medium: "default",
  low: "secondary",
} as const;

export function TodayTasks() {
  const { data: tasks = [], isLoading, error } = useDueTodayTasks();
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

  const completedCount = tasks.filter(t => t.completed).length;
  const totalCount = tasks.length;
  const completionPercentage = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

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
          Unable to load today's tasks. Please check your backend connection.
        </p>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="px-4 py-8 text-center">
        <Calendar className="w-12 h-12 mx-auto mb-3 text-muted-foreground/50" />
        <p className="text-sm text-muted-foreground">
          No tasks due today. Enjoy your free time!
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* Progress Header */}
      <div className="px-4 py-3 bg-muted/30 border-b border-border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Today's Progress</span>
          <span className="text-xs text-muted-foreground">
            {completedCount} of {totalCount} completed
          </span>
        </div>
        <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
          <div
            className={cn(
              "h-full transition-all duration-300",
              completionPercentage === 100 ? "bg-green-500" : "bg-primary"
            )}
            style={{ width: `${completionPercentage}%` }}
          />
        </div>
      </div>

      {/* Tasks List */}
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
          </div>
        ))}
      </div>
    </div>
  );
}
