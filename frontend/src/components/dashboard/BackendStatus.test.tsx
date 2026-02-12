import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@/test/test-utils';
import { BackendStatus } from './BackendStatus';

describe('BackendStatus', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    // Mock AbortSignal.timeout which isn't available in jsdom
    if (!AbortSignal.timeout) {
      (AbortSignal as any).timeout = vi.fn(() => new AbortController().signal);
    }
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('shows connected status when backend responds OK', async () => {
    (global.fetch as any).mockResolvedValue({ ok: true });

    render(<BackendStatus />);

    await waitFor(() => {
      expect(screen.getByText('Live')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('shows offline status when backend fails', async () => {
    (global.fetch as any).mockRejectedValue(new Error('Network error'));

    render(<BackendStatus />);

    await waitFor(() => {
      expect(screen.getByText('Offline')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('shows offline when response is not ok', async () => {
    (global.fetch as any).mockResolvedValue({ ok: false });

    render(<BackendStatus />);

    await waitFor(() => {
      expect(screen.getByText('Offline')).toBeInTheDocument();
    }, { timeout: 3000 });
  });
});
