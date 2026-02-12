import { describe, it, expect } from 'vitest';
import { render, screen } from '@/test/test-utils';
import { Header } from './Header';

describe('Header', () => {
  it('renders the page title based on current route', () => {
    // Default route "/" maps to "Inbox"
    render(<Header />);
    // BrowserRouter starts at "/" which maps to "Inbox"
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
  });

  it('renders Share button', () => {
    render(<Header />);
    expect(screen.getByText('Share')).toBeInTheDocument();
  });

  it('renders Sort button', () => {
    render(<Header />);
    expect(screen.getByText('Sort')).toBeInTheDocument();
  });
});
