import { useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const presets = [
  { label: 'Today', value: '1d' },
  { label: '7 days', value: '7d' },
  { label: '30 days', value: '30d' },
  { label: '90 days', value: '90d' },
];

export function PeriodFilter() {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentPeriod = searchParams.get('period') || '30d';
  const hasCustomRange = searchParams.has('date_from');

  function setPeriod(period: string) {
    const next = new URLSearchParams();
    next.set('period', period);
    setSearchParams(next);
  }

  return (
    <div className="flex items-center gap-1">
      {presets.map((preset) => (
        <Button
          key={preset.value}
          variant={!hasCustomRange && currentPeriod === preset.value ? 'secondary' : 'ghost'}
          size="sm"
          onClick={() => setPeriod(preset.value)}
          className={cn(
            'text-xs',
            !hasCustomRange && currentPeriod === preset.value && 'bg-secondary'
          )}
        >
          {preset.label}
        </Button>
      ))}
    </div>
  );
}
