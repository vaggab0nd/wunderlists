import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import {
  useTasks,
  useCreateTask,
  useUpdateTask,
  useDeleteTask,
  Task,
} from './useRailwayData';

// Mock fetch globally
global.fetch = vi.fn();

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useRailwayData hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('useTasks', () => {
    it('fetches tasks successfully', async () => {
      const mockTasks: Task[] = [
        {
          id: '1',
          title: 'Test Task',
          completed: false,
          priority: 'high',
        },
      ];

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockTasks,
      });

      const { result } = renderHook(() => useTasks(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toEqual(mockTasks);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/tasks')
      );
    });

    it('handles fetch errors', async () => {
      (global.fetch as any).mockRejectedValueOnce(
        new Error('Network error')
      );

      const { result } = renderHook(() => useTasks(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => expect(result.current.isError).toBe(true), {
        timeout: 3000,
      });

      expect(result.current.error).toBeDefined();
    });
  });

  describe('useCreateTask', () => {
    it('creates a task successfully', async () => {
      const newTask: Task = {
        id: '2',
        title: 'New Task',
        completed: false,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => newTask,
      });

      const { result } = renderHook(() => useCreateTask(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({ title: 'New Task', completed: false });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toEqual(newTask);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/tasks'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });
  });

  describe('useUpdateTask', () => {
    it('updates a task successfully', async () => {
      const updatedTask: Task = {
        id: '1',
        title: 'Updated Task',
        completed: true,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => updatedTask,
      });

      const { result } = renderHook(() => useUpdateTask(), {
        wrapper: createWrapper(),
      });

      result.current.mutate({
        id: '1',
        title: 'Updated Task',
        completed: true,
      });

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(result.current.data).toEqual(updatedTask);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/tasks/1'),
        expect.objectContaining({
          method: 'PATCH',
        })
      );
    });
  });

  describe('useDeleteTask', () => {
    it('deletes a task successfully', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
      });

      const { result } = renderHook(() => useDeleteTask(), {
        wrapper: createWrapper(),
      });

      result.current.mutate('1');

      await waitFor(() => expect(result.current.isSuccess).toBe(true));

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/tasks/1'),
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });
  });
});
