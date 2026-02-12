import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, waitFor } from '@/test/test-utils';
import { HabitTracker } from './HabitTracker';

describe('HabitTracker', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders the Habits heading', () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<HabitTracker />);
    expect(screen.getByText('Habits')).toBeInTheDocument();
  });

  it('renders day column headers', () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<HabitTracker />);
    expect(screen.getByText('Mon')).toBeInTheDocument();
    expect(screen.getByText('Tue')).toBeInTheDocument();
    expect(screen.getByText('Wed')).toBeInTheDocument();
    expect(screen.getByText('Thu')).toBeInTheDocument();
    expect(screen.getByText('Fri')).toBeInTheDocument();
    expect(screen.getByText('Sat')).toBeInTheDocument();
    expect(screen.getByText('Sun')).toBeInTheDocument();
  });

  it('renders fallback habits when API returns empty', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<HabitTracker />);

    await waitFor(() => {
      expect(screen.getByText('Hydration')).toBeInTheDocument();
      expect(screen.getByText('Reading')).toBeInTheDocument();
      expect(screen.getByText('Exercise')).toBeInTheDocument();
      expect(screen.getByText('Sleep 8hrs')).toBeInTheDocument();
    });
  });

  it('renders streak column header', () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<HabitTracker />);
    expect(screen.getByText('Streak')).toBeInTheDocument();
  });

  it('renders Habit column header', () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<HabitTracker />);
    expect(screen.getByText('Habit')).toBeInTheDocument();
  });
});
