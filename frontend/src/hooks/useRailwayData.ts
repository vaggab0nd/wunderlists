import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

const RAILWAY_API_URL = import.meta.env.VITE_RAILWAY_API_URL || "https://passionate-perception-production.up.railway.app/api";

export interface User {
  id: string;
  name: string;
  email: string;
  created_at?: string;
  updated_at?: string;
}

export interface Task {
  id: string;
  title: string;
  completed: boolean;
  due_date?: string;
  priority?: "low" | "medium" | "high";
  category?: string;
  assigned_to?: string; // User ID
  assigned_user?: User; // Populated user object
  is_travel_day?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Habit {
  id: string;
  name: string;
  icon: string;
  streak: number;
  completed: boolean;
  completed_days?: boolean[];
  week_progress?: boolean[];
  created_at?: string;
  updated_at?: string;
}

export interface Note {
  id: string;
  title: string;
  content: string;
  color: string;
  created_at?: string;
  updated_at?: string;
}

export interface CalendarEvent {
  id: string;
  title: string;
  start_time: string;
  end_time: string;
  description?: string;
  location?: string;
  google_event_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface WeatherAlert {
  id: string;
  task_id: string;
  location: string;
  date: string;
  weather_condition: string;
  temperature: number;
  alert_type: "warning" | "info";
  message: string;
  created_at?: string;
}

export interface TaskSuggestion {
  id: string;
  task_id: string;
  suggested_priority: "low" | "medium" | "high";
  reason: string;
  confidence_score: number;
}

async function fetchResource<T>(resource: string): Promise<T[]> {
  const response = await fetch(`${RAILWAY_API_URL}/${resource}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${resource}: ${response.statusText}`);
  }
  const data = await response.json();
  // Ensure we always return an array even if the API returns an object
  return Array.isArray(data) ? data : [];
}

async function createResource<T>(resource: string, body: Partial<T>): Promise<T> {
  const response = await fetch(`${RAILWAY_API_URL}/${resource}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`Failed to create ${resource}: ${response.statusText}`);
  }
  return response.json();
}

async function updateResource<T>(resource: string, id: string, body: Partial<T>): Promise<T> {
  const response = await fetch(`${RAILWAY_API_URL}/${resource}/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`Failed to update ${resource}: ${response.statusText}`);
  }
  return response.json();
}

async function deleteResource(resource: string, id: string): Promise<void> {
  const response = await fetch(`${RAILWAY_API_URL}/${resource}/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) {
    throw new Error(`Failed to delete ${resource}: ${response.statusText}`);
  }
}

// Tasks hooks
export function useTasks() {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: () => fetchResource<Task>('tasks'),
    retry: 1,
    staleTime: 30000,
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (task: Partial<Task>) => createResource<Task>('tasks', task),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] }),
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...task }: Partial<Task> & { id: string }) => 
      updateResource<Task>('tasks', id, task),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] }),
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteResource('tasks', id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks'] }),
  });
}

// Smart task filtering hooks
export function usePrioritizedTasks() {
  return useQuery({
    queryKey: ['tasks', 'prioritized'],
    queryFn: () => fetchResource<Task>('tasks/prioritized'),
    retry: 1,
    staleTime: 30000,
  });
}

export function useOverdueTasks() {
  return useQuery({
    queryKey: ['tasks', 'overdue'],
    queryFn: () => fetchResource<Task>('tasks/overdue'),
    retry: 1,
    staleTime: 30000,
  });
}

export function useDueTodayTasks() {
  return useQuery({
    queryKey: ['tasks', 'due-today'],
    queryFn: () => fetchResource<Task>('tasks/due-today'),
    retry: 1,
    staleTime: 30000,
  });
}

// Habits hooks
export function useHabits() {
  return useQuery({
    queryKey: ['habits'],
    queryFn: () => fetchResource<Habit>('habits'),
    retry: 1,
    staleTime: 30000,
  });
}

export function useCreateHabit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (habit: Partial<Habit>) => createResource<Habit>('habits', habit),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['habits'] }),
  });
}

export function useUpdateHabit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...habit }: Partial<Habit> & { id: string }) => 
      updateResource<Habit>('habits', id, habit),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['habits'] }),
  });
}

export function useToggleHabit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await fetch(`${RAILWAY_API_URL}/habits/${id}/toggle`, {
        method: 'PUT',
      });
      if (!response.ok) {
        throw new Error(`Failed to toggle habit: ${response.statusText}`);
      }
      return response.json();
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['habits'] }),
  });
}

export function useDeleteHabit() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteResource('habits', id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['habits'] }),
  });
}

// Notes hooks
export function useNotes() {
  return useQuery({
    queryKey: ['notes'],
    queryFn: () => fetchResource<Note>('notes'),
    retry: 1,
    staleTime: 30000,
  });
}

export function useCreateNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (note: Partial<Note>) => createResource<Note>('notes', note),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notes'] }),
  });
}

export function useUpdateNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...note }: Partial<Note> & { id: string }) => 
      updateResource<Note>('notes', id, note),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notes'] }),
  });
}

export function useDeleteNote() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteResource('notes', id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notes'] }),
  });
}

// Users hooks
export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => fetchResource<User>('users'),
    retry: 1,
    staleTime: 30000,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (user: Partial<User>) => createResource<User>('users', user),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...user }: Partial<User> & { id: string }) =>
      updateResource<User>('users', id, user),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteResource('users', id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  });
}

// Calendar Events hooks
export function useCalendarEvents() {
  return useQuery({
    queryKey: ['calendar-events'],
    queryFn: () => fetchResource<CalendarEvent>('calendar/events'),
    retry: 1,
    staleTime: 30000,
  });
}

export function useSyncGoogleCalendar() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const response = await fetch(`${RAILWAY_API_URL}/calendar/sync`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Failed to sync calendar: ${response.statusText}`);
      }
      return response.json();
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['calendar-events'] }),
  });
}

export function useConnectGoogleCalendar() {
  return useMutation({
    mutationFn: async (authCode: string) => {
      const response = await fetch(`${RAILWAY_API_URL}/calendar/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ auth_code: authCode }),
      });
      if (!response.ok) {
        throw new Error(`Failed to connect calendar: ${response.statusText}`);
      }
      return response.json();
    },
  });
}

// Weather Alerts hooks
export function useWeatherAlerts() {
  return useQuery({
    queryKey: ['weather-alerts'],
    queryFn: async () => {
      const response = await fetch(`${RAILWAY_API_URL}/weather/alerts`);
      if (!response.ok) {
        throw new Error(`Failed to fetch weather alerts: ${response.statusText}`);
      }
      const data = await response.json();
      // API returns { alerts: [], summary: {...} } - extract the alerts array
      return Array.isArray(data) ? data : (data.alerts || []);
    },
    retry: 1,
    staleTime: 300000, // 5 minutes
  });
}

export function useRefreshWeatherAlerts() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const response = await fetch(`${RAILWAY_API_URL}/weather/refresh`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Failed to refresh weather alerts: ${response.statusText}`);
      }
      return response.json();
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['weather-alerts'] }),
  });
}

// Current Weather hooks (simpler endpoint - always shows Dublin & Île de Ré)
export function useCurrentWeather() {
  return useQuery({
    queryKey: ['weather-current'],
    queryFn: () => fetchResource<WeatherAlert>('weather/current'),
    retry: 1,
    staleTime: 300000, // 5 minutes
  });
}

export function useRefreshCurrentWeather() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const response = await fetch(`${RAILWAY_API_URL}/weather/current`, {
        method: 'GET',
      });
      if (!response.ok) {
        throw new Error(`Failed to refresh weather: ${response.statusText}`);
      }
      return response.json();
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['weather-current'] }),
  });
}

// Task Suggestions hooks
export function useTaskSuggestions() {
  return useQuery({
    queryKey: ['task-suggestions'],
    queryFn: async () => {
      try {
        const response = await fetch(`${RAILWAY_API_URL}/tasks/suggestions`);
        if (!response.ok) {
          // Return empty array on error instead of throwing
          return [];
        }
        const data = await response.json();
        return Array.isArray(data) ? data : [];
      } catch {
        return [];
      }
    },
    retry: 0, // Don't retry as endpoint may not exist
    staleTime: 60000, // 1 minute
  });
}

export function useGenerateTaskSuggestions() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const response = await fetch(`${RAILWAY_API_URL}/tasks/generate-suggestions`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`Failed to generate task suggestions: ${response.statusText}`);
      }
      return response.json();
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['task-suggestions'] }),
  });
}
