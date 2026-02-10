import { useState } from "react";
import { Check, Star, Plus, Loader2, User as UserIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useTasks, useCreateTask, useUpdateTask, useUsers, Task } from "@/hooks/useRailwayData";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

// Fallback data for when DB is empty or loading
const fallbackTasks: Task[] = [
  { id: "1", title: "Review project proposal", completed: true, priority: "high", due_date: "Today" },
  { id: "2", title: "Update weekly goals", completed: false, due_date: "Today", priority: "medium" },
  { id: "3", title: "Call with design team", completed: false, due_date: "Today", priority: "low" },
  { id: "4", title: "Draft Wunderlist article", completed: false, due_date: "Tomorrow", priority: "high" },
  { id: "5", title: "Grocery shopping", completed: false, due_date: "Sunday", priority: "medium" },
];

// Group tasks by due date
function groupTasksByDate(tasks: Task[]): Record<string, Task[]> {
  const groups: Record<string, Task[]> = {};
  
  tasks.forEach(task => {
    const date = task.due_date || "No Date";
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(task);
  });
  
  return groups;
}

export function TaskList() {
  const { data: tasksFromDb, isLoading, error } = useTasks();
  const { data: users = [] } = useUsers();
  const createTask = useCreateTask();
  const updateTask = useUpdateTask();
  const [newTask, setNewTask] = useState("");
  const [selectedUserId, setSelectedUserId] = useState<string>("");
  const [starredTasks, setStarredTasks] = useState<Set<string>>(new Set(["4"]));
  const [localTasks, setLocalTasks] = useState<Task[]>(fallbackTasks);

  // Use DB data if available, otherwise use local state (which starts with fallback)
  const tasks = (tasksFromDb && tasksFromDb.length > 0) ? tasksFromDb : localTasks;
  const isUsingFallback = !tasksFromDb || tasksFromDb.length === 0;
  const groupedTasks = groupTasksByDate(tasks);

  const toggleTask = (task: Task) => {
    if (!isUsingFallback) {
      updateTask.mutate({ id: task.id, completed: !task.completed });
    } else {
      // Update local state when using fallback data
      setLocalTasks(prev => prev.map(t =>
        t.id === task.id ? { ...t, completed: !t.completed } : t
      ));
    }
  };

  const toggleStar = (taskId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setStarredTasks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(taskId)) {
        newSet.delete(taskId);
      } else {
        newSet.add(taskId);
      }
      return newSet;
    });
  };

  const addTask = () => {
    if (!newTask.trim()) return;
    if (!isUsingFallback) {
      createTask.mutate({
        title: newTask,
        completed: false,
        priority: "medium",
        due_date: "Today",
        assigned_to: selectedUserId || undefined
      });
    } else {
      // Add to local state when using fallback data
      const newTaskObj: Task = {
        id: Date.now().toString(),
        title: newTask,
        completed: false,
        priority: "medium",
        due_date: "Today",
        assigned_to: selectedUserId || undefined
      };
      setLocalTasks(prev => [...prev, newTaskObj]);
    }
    setNewTask("");
    setSelectedUserId("");
  };

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map(n => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const getListLabel = (task: Task): string => {
    if (task.priority === "high") return "Work To-Dos";
    if (task.priority === "medium") return "Shopping List";
    return "Family Chores";
  };

  return (
    <div className="flex-1 bg-card rounded-lg shadow-sm border border-border overflow-hidden">
      {/* Task Input */}
      <div className="p-4 border-b border-border bg-muted/30">
        <div className="flex gap-2 flex-wrap">
          <Input
            placeholder="Add a task..."
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && addTask()}
            className="bg-background border-border flex-1 min-w-[200px]"
          />
          <Select value={selectedUserId} onValueChange={setSelectedUserId}>
            <SelectTrigger className="w-[180px] bg-background">
              <SelectValue placeholder="Assign to..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="unassigned">Unassigned</SelectItem>
              {users.map((user) => (
                <SelectItem key={user.id} value={user.id}>
                  {user.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            onClick={addTask}
            disabled={createTask.isPending}
            className="bg-primary hover:bg-primary/90 text-primary-foreground"
          >
            {createTask.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Plus className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
        </div>
      )}

      {/* Task Groups */}
      <div className="max-h-[calc(100vh-300px)] overflow-y-auto">
        {Object.entries(groupedTasks).map(([date, dateTasks]) => (
          <div key={date}>
            {/* Date Header */}
            <div className="date-header sticky top-0 z-10">
              {date.toUpperCase()}
            </div>
            
            {/* Tasks */}
            <div className="divide-y divide-border">
              {dateTasks.map((task) => (
                <div 
                  key={task.id}
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 task-item cursor-pointer",
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
                  
                  {/* List Badge */}
                  <span className="list-badge hidden sm:inline-block">
                    {getListLabel(task)}
                  </span>

                  {/* Assignee Avatar */}
                  {task.assigned_user ? (
                    <Avatar className="w-6 h-6">
                      <AvatarFallback className="bg-primary/20 text-primary text-xs">
                        {getInitials(task.assigned_user.name)}
                      </AvatarFallback>
                    </Avatar>
                  ) : task.assigned_to && users.length > 0 ? (
                    <Avatar className="w-6 h-6">
                      <AvatarFallback className="bg-primary/20 text-primary text-xs">
                        {getInitials(users.find(u => u.id === task.assigned_to)?.name || "?")}
                      </AvatarFallback>
                    </Avatar>
                  ) : (
                    <div className="w-6 h-6 rounded-full bg-muted flex items-center justify-center">
                      <UserIcon className="w-3 h-3 text-muted-foreground" />
                    </div>
                  )}
                  
                  {/* Star */}
                  <button
                    onClick={(e) => toggleStar(task.id, e)}
                    className={cn(
                      "star-button",
                      starredTasks.has(task.id) && "starred"
                    )}
                  >
                    <Star className={cn(
                      "w-4 h-4",
                      starredTasks.has(task.id) && "fill-current"
                    )} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Error State */}
      {error && (
        <div className="px-4 py-2 bg-destructive/10 text-destructive text-sm">
          Using demo data - connect to Railway backend
        </div>
      )}
    </div>
  );
}