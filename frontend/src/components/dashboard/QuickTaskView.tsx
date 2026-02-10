import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useOverdueTasks, useDueTodayTasks } from "@/hooks/useRailwayData";
import { AlertCircle, Calendar, ArrowRight, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";

export const QuickTaskView = () => {
  const { data: overdueTasks = [], isLoading: overdueLoading } = useOverdueTasks();
  const { data: todayTasks = [], isLoading: todayLoading } = useDueTodayTasks();
  const navigate = useNavigate();

  const incompleteTodayTasks = todayTasks.filter(t => !t.completed);
  const incompleteOverdueTasks = overdueTasks.filter(t => !t.completed);

  if (overdueLoading || todayLoading) {
    return (
      <Card>
        <CardContent className="py-6 text-center">
          <Loader2 className="w-6 h-6 animate-spin text-muted-foreground mx-auto" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Quick Overview</CardTitle>
        <CardDescription>Your task status at a glance</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Overdue Tasks */}
        <div className="p-3 rounded-lg border border-destructive/20 bg-destructive/5">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-destructive" />
              <span className="text-sm font-medium">Overdue</span>
            </div>
            <Badge variant="destructive" className="text-xs">
              {incompleteOverdueTasks.length}
            </Badge>
          </div>
          {incompleteOverdueTasks.length > 0 ? (
            <div className="space-y-1 mt-2">
              {incompleteOverdueTasks.slice(0, 3).map((task) => (
                <div key={task.id} className="text-xs text-muted-foreground truncate">
                  • {task.title}
                </div>
              ))}
              {incompleteOverdueTasks.length > 3 && (
                <div className="text-xs text-muted-foreground">
                  + {incompleteOverdueTasks.length - 3} more
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground mt-1">
              All caught up! 🎉
            </p>
          )}
        </div>

        {/* Today's Tasks */}
        <div className="p-3 rounded-lg border border-primary/20 bg-primary/5">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium">Due Today</span>
            </div>
            <Badge variant="default" className="text-xs">
              {incompleteTodayTasks.length}
            </Badge>
          </div>
          {incompleteTodayTasks.length > 0 ? (
            <div className="space-y-1 mt-2">
              {incompleteTodayTasks.slice(0, 3).map((task) => (
                <div key={task.id} className="text-xs text-muted-foreground truncate">
                  • {task.title}
                </div>
              ))}
              {incompleteTodayTasks.length > 3 && (
                <div className="text-xs text-muted-foreground">
                  + {incompleteTodayTasks.length - 3} more
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-muted-foreground mt-1">
              Nothing due today
            </p>
          )}
        </div>

        {/* View All Button */}
        <Button
          variant="outline"
          className="w-full"
          onClick={() => navigate('/tasks')}
        >
          View All Tasks
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </CardContent>
    </Card>
  );
};
