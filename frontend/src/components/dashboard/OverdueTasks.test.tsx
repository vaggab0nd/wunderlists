import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, waitFor } from '@/test/test-utils';
import { OverdueTasks } from './OverdueTasks';

describe('OverdueTasks', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('shows loading spinner initially', () => {
    (global.fetch as any).mockReturnValue(new Promise(() => {}));

    const { container } = render(<OverdueTasks />);
    expect(container.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('shows all caught up message when no overdue tasks', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<OverdueTasks />);

    await waitFor(() => {
      expect(screen.getByText(/all caught up/i)).toBeInTheDocument();
    });
  });

  it('renders overdue tasks when available', async () => {
    const overdueTasks = [
      {
        id: '1',
        title: 'Overdue task 1',
        completed: false,
        priority: 'high',
        due_date: '2024-01-01',
        days_overdue: 5,
      },
    ];

    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => overdueTasks,
    });

    render(<OverdueTasks />);

    await waitFor(() => {
      expect(screen.getByText('Overdue task 1')).toBeInTheDocument();
    });
  });

  it('shows error message when API fails', async () => {
    (global.fetch as any).mockRejectedValue(new Error('Network error'));

    render(<OverdueTasks />);

    await waitFor(() => {
      expect(screen.getByText(/unable to load/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('displays priority badges on tasks', async () => {
    const tasks = [
      {
        id: '1',
        title: 'High priority task',
        completed: false,
        priority: 'high',
        due_date: '2024-01-01',
      },
    ];

    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => tasks,
    });

    render(<OverdueTasks />);

    await waitFor(() => {
      expect(screen.getByText('high')).toBeInTheDocument();
    });
  });
});
