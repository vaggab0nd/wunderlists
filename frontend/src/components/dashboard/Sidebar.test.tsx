import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@/test/test-utils';
import { Sidebar } from './Sidebar';

describe('Sidebar', () => {
  it('renders the Wunderlists brand', () => {
    render(<Sidebar isOpen={true} />);
    expect(screen.getByText('Wunderlists')).toBeInTheDocument();
  });

  it('renders smart list navigation items', () => {
    render(<Sidebar isOpen={true} />);
    expect(screen.getByText('Inbox')).toBeInTheDocument();
    expect(screen.getByText('Assigned to me')).toBeInTheDocument();
    expect(screen.getByText('Starred')).toBeInTheDocument();
    expect(screen.getByText('Today')).toBeInTheDocument();
    expect(screen.getByText('Week')).toBeInTheDocument();
  });

  it('renders folder sections', () => {
    render(<Sidebar isOpen={true} />);
    expect(screen.getByText('Household')).toBeInTheDocument();
    expect(screen.getByText('Work')).toBeInTheDocument();
    expect(screen.getByText('Personal')).toBeInTheDocument();
  });

  it('shows expanded folder contents by default for Household', () => {
    render(<Sidebar isOpen={true} />);
    // Household and Personal are expanded by default
    expect(screen.getByText('Family Chores')).toBeInTheDocument();
    expect(screen.getByText('Shopping List')).toBeInTheDocument();
  });

  it('toggles folder expansion on click', () => {
    render(<Sidebar isOpen={true} />);

    // Work is collapsed by default, so its lists shouldn't be visible
    expect(screen.queryByText('Projects')).not.toBeInTheDocument();

    // Click Work folder to expand
    fireEvent.click(screen.getByText('Work'));
    expect(screen.getByText('Projects')).toBeInTheDocument();
    expect(screen.getByText('Meetings')).toBeInTheDocument();
  });

  it('renders Create new list button', () => {
    render(<Sidebar isOpen={true} />);
    expect(screen.getByText('Create new list')).toBeInTheDocument();
  });

  it('renders navigation links with correct paths', () => {
    render(<Sidebar isOpen={true} />);

    const inboxLink = screen.getByText('Inbox').closest('a');
    expect(inboxLink).toHaveAttribute('href', '/');

    const weekLink = screen.getByText('Week').closest('a');
    expect(weekLink).toHaveAttribute('href', '/tasks');
  });

  it('calls onClose callback', () => {
    const onClose = vi.fn();
    render(<Sidebar isOpen={true} onClose={onClose} />);

    // The mobile close button
    const closeButtons = screen.getAllByRole('button');
    // Find the X button (it's the one in the header area for mobile)
    const closeButton = closeButtons.find(btn => btn.querySelector('.lucide-x'));
    if (closeButton) {
      fireEvent.click(closeButton);
      expect(onClose).toHaveBeenCalled();
    }
  });
});
