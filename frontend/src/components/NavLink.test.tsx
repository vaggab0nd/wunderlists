import { describe, it, expect } from 'vitest';
import { render, screen } from '@/test/test-utils';
import { NavLink } from './NavLink';

describe('NavLink', () => {
  it('renders a link with the correct text', () => {
    render(<NavLink to="/tasks">Tasks</NavLink>);
    expect(screen.getByText('Tasks')).toBeInTheDocument();
  });

  it('renders with correct href', () => {
    render(<NavLink to="/tasks">Tasks</NavLink>);
    const link = screen.getByRole('link', { name: 'Tasks' });
    expect(link).toHaveAttribute('href', '/tasks');
  });

  it('applies custom className', () => {
    render(
      <NavLink to="/tasks" className="custom-class">
        Tasks
      </NavLink>
    );
    const link = screen.getByRole('link', { name: 'Tasks' });
    expect(link).toHaveClass('custom-class');
  });
});
