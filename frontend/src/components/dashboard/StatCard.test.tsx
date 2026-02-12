import { describe, it, expect } from 'vitest';
import { render, screen } from '@/test/test-utils';
import { StatCard } from './StatCard';
import { CheckCircle } from 'lucide-react';

describe('StatCard', () => {
  it('renders title and value', () => {
    render(
      <StatCard
        title="Total Tasks"
        value={42}
        icon={CheckCircle}
      />
    );

    expect(screen.getByText('Total Tasks')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('renders subtitle when provided', () => {
    render(
      <StatCard
        title="Tasks"
        value={10}
        subtitle="This week"
        icon={CheckCircle}
      />
    );

    expect(screen.getByText('This week')).toBeInTheDocument();
  });

  it('renders trend when provided', () => {
    render(
      <StatCard
        title="Tasks"
        value={10}
        icon={CheckCircle}
        trend={{ value: 15, positive: true }}
      />
    );

    expect(screen.getByText('+15%')).toBeInTheDocument();
    expect(screen.getByText('vs last week')).toBeInTheDocument();
  });

  it('renders negative trend', () => {
    render(
      <StatCard
        title="Tasks"
        value={5}
        icon={CheckCircle}
        trend={{ value: -10, positive: false }}
      />
    );

    expect(screen.getByText('-10%')).toBeInTheDocument();
  });

  it('renders string values', () => {
    render(
      <StatCard
        title="Status"
        value="Active"
        icon={CheckCircle}
      />
    );

    expect(screen.getByText('Active')).toBeInTheDocument();
  });
});
