import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@/test/test-utils';
import { TaskList } from './TaskList';

describe('TaskList', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders task input field', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<TaskList />);

    expect(screen.getByPlaceholderText('Add a task...')).toBeInTheDocument();
  });

  it('renders fallback tasks when no data from API', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<TaskList />);

    // Should render fallback tasks
    await waitFor(() => {
      expect(screen.getByText('Review project proposal')).toBeInTheDocument();
      expect(screen.getByText('Update weekly goals')).toBeInTheDocument();
    });
  });

  it('renders tasks from API when available', async () => {
    const mockTasks = [
      { id: '1', title: 'API Task 1', completed: false, priority: 'high', due_date: 'Today' },
      { id: '2', title: 'API Task 2', completed: true, priority: 'low', due_date: 'Today' },
    ];

    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockTasks,
    });

    render(<TaskList />);

    await waitFor(() => {
      expect(screen.getByText('API Task 1')).toBeInTheDocument();
      expect(screen.getByText('API Task 2')).toBeInTheDocument();
    });
  });

  it('shows error message when API fails', async () => {
    (global.fetch as any).mockRejectedValue(new Error('Network error'));

    render(<TaskList />);

    await waitFor(() => {
      expect(screen.getByText(/demo data/i)).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('allows typing in the task input', () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<TaskList />);

    const input = screen.getByPlaceholderText('Add a task...');
    fireEvent.change(input, { target: { value: 'New task text' } });
    expect(input).toHaveValue('New task text');
  });

  it('has an add task button', () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<TaskList />);

    // The button with Plus icon
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });
});
