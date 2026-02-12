import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@/test/test-utils';
import { WeatherAlerts } from './WeatherAlerts';

describe('WeatherAlerts', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('shows loading state initially', () => {
    // Never resolve the fetch to keep it in loading state
    (global.fetch as any).mockReturnValue(new Promise(() => {}));

    render(<WeatherAlerts />);
    expect(screen.getByText('Loading weather...')).toBeInTheDocument();
  });

  it('shows no data message when API returns empty array', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<WeatherAlerts />);

    await waitFor(() => {
      expect(screen.getByText('No weather data available')).toBeInTheDocument();
    });
  });

  it('renders Current Weather title', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<WeatherAlerts />);

    await waitFor(() => {
      expect(screen.getByText('Current Weather')).toBeInTheDocument();
    });
  });

  it('renders Dublin & Ile de Re description', async () => {
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => [],
    });

    render(<WeatherAlerts />);

    await waitFor(() => {
      // The subtitle is always rendered on the empty state card
      const descriptions = screen.getAllByText(/Dublin/);
      expect(descriptions.length).toBeGreaterThan(0);
    });
  });

  it('renders weather data when API returns array of alerts', async () => {
    // fetchResource expects an array response to pass through directly
    const weatherData = [
      {
        id: '1',
        location: 'Dublin, Ireland',
        temperature: 12.5,
        weather_condition: 'Partly cloudy',
        alert_type: 'info',
        message: 'Bring an umbrella',
      },
    ];

    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => weatherData,
    });

    render(<WeatherAlerts />);

    await waitFor(() => {
      expect(screen.getByText('Dublin, Ireland')).toBeInTheDocument();
      expect(screen.getByText('12.5°C')).toBeInTheDocument();
      expect(screen.getByText('Partly cloudy')).toBeInTheDocument();
    });
  });
});
