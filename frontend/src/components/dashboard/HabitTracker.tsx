import { Flame, Droplets, BookOpen, Dumbbell, Moon, Loader2, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";
import { useHabits, useToggleHabit, Habit } from "@/hooks/useRailwayData";

const iconMap: Record<string, LucideIcon> = {
  droplets: Droplets,
  book: BookOpen,
  dumbbell: Dumbbell,
  moon: Moon,
  circle: Flame,
  flame: Flame,
};

// Fallback data
const fallbackHabits: Habit[] = [
  { id: "1", name: "Hydration", icon: "droplets", streak: 12, completed: true, week_progress: [true, true, true, true, true, false, false] },
  { id: "2", name: "Reading", icon: "book", streak: 8, completed: false, week_progress: [true, true, false, true, true, false, false] },
  { id: "3", name: "Exercise", icon: "dumbbell", streak: 5, completed: true, week_progress: [true, false, true, true, true, false, false] },
  { id: "4", name: "Sleep 8hrs", icon: "moon", streak: 3, completed: false, week_progress: [false, true, true, true, false, false, false] },
];

const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export function HabitTracker() {
  const { data: habitsFromDb, isLoading, error } = useHabits();
  const toggleHabit = useToggleHabit();

  // Use DB data if available, otherwise use fallback
  const habits = (habitsFromDb && habitsFromDb.length > 0) ? habitsFromDb : fallbackHabits;
  const isUsingFallback = !habitsFromDb || habitsFromDb.length === 0;

  const handleToggle = (habit: Habit) => {
    if (!isUsingFallback) {
      toggleHabit.mutate(habit.id);
    }
  };

  // Support both completed_days and week_progress field names
  const getWeekProgress = (habit: Habit): boolean[] => {
    return habit.week_progress || habit.completed_days || [];
  };

  return (
    <div className="bg-card rounded-lg border border-border overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        <div>
          <h3 className="text-lg font-semibold">Habits</h3>
          <p className="text-sm text-muted-foreground">
            {isLoading ? "Loading..." : "Track your daily habits"}
          </p>
        </div>
        {isLoading && <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />}
      </div>

      {/* Habits Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted/30">
              <th className="text-left px-4 py-3 text-sm font-medium text-muted-foreground">Habit</th>
              {days.map(day => (
                <th key={day} className="px-2 py-3 text-center text-xs font-medium text-muted-foreground w-12">
                  {day}
                </th>
              ))}
              <th className="px-4 py-3 text-right text-sm font-medium text-muted-foreground">Streak</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {habits.map((habit) => {
              const Icon = iconMap[habit.icon?.toLowerCase()] || Flame;
              const weekProgress = getWeekProgress(habit);
              
              return (
                <tr key={habit.id} className="task-item">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => handleToggle(habit)}
                        disabled={toggleHabit.isPending}
                        className={cn(
                          "w-8 h-8 rounded-lg flex items-center justify-center transition-all",
                          habit.completed 
                            ? "bg-accent text-accent-foreground" 
                            : "bg-secondary text-muted-foreground hover:bg-secondary/80"
                        )}
                      >
                        <Icon className="w-4 h-4" />
                      </button>
                      <span className="text-sm font-medium">{habit.name}</span>
                    </div>
                  </td>
                  {days.map((_, i) => (
                    <td key={i} className="px-2 py-3 text-center">
                      <div className={cn(
                        "w-6 h-6 mx-auto rounded flex items-center justify-center transition-colors",
                        weekProgress[i] 
                          ? "bg-accent text-accent-foreground" 
                          : "bg-muted"
                      )}>
                        {weekProgress[i] && <Check className="w-3 h-3" />}
                      </div>
                    </td>
                  ))}
                  <td className="px-4 py-3 text-right">
                    <span className="inline-flex items-center gap-1 text-sm font-medium text-primary">
                      <Flame className="w-4 h-4" />
                      {habit.streak || 0}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Error State */}
      {error && (
        <div className="px-4 py-2 bg-destructive/10 text-destructive text-sm">
          Using demo data
        </div>
      )}
    </div>
  );
}