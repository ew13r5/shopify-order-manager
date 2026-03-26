import { useSearchParams } from 'react-router-dom';
import { usePayouts, useAdjustments } from '@/hooks/usePayouts';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PeriodFilter } from '@/components/shared/PeriodFilter';
import { cn } from '@/lib/utils';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';

const PERIOD_OPTIONS = [
  { label: 'Day', value: 'day' },
  { label: 'Week', value: 'week' },
  { label: 'Month', value: 'month' },
];

function PeriodToggle() {
  const [searchParams, setSearchParams] = useSearchParams();
  const groupBy = searchParams.get('group_by') || 'day';

  function setGroupBy(value: string) {
    const next = new URLSearchParams(searchParams);
    next.set('group_by', value);
    setSearchParams(next, { replace: true });
  }

  return (
    <div className="flex items-center gap-1 rounded-lg border p-1">
      {PERIOD_OPTIONS.map((opt) => (
        <Button
          key={opt.value}
          variant={groupBy === opt.value ? 'secondary' : 'ghost'}
          size="sm"
          className="text-xs h-7"
          onClick={() => setGroupBy(opt.value)}
        >
          {opt.label}
        </Button>
      ))}
    </div>
  );
}

function AdjustmentsSection() {
  const { data: adjustments, isLoading } = useAdjustments();

  if (isLoading) return <Skeleton height={100} baseColor="#1f2937" highlightColor="#374151" borderRadius={12} />;
  if (!adjustments?.length) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Adjustments</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="px-4 py-2 text-left font-medium">Type</th>
              <th className="px-4 py-2 text-right font-medium">Amount</th>
              <th className="px-4 py-2 text-left font-medium">Reason</th>
              <th className="px-4 py-2 text-left font-medium">Date</th>
            </tr>
          </thead>
          <tbody>
            {adjustments.map((adj) => (
              <tr key={adj.id} className="border-b">
                <td className="px-4 py-3">
                  <Badge
                    variant={adj.type === 'chargeback' ? 'destructive' : 'secondary'}
                    className="text-xs"
                  >
                    {adj.type}
                  </Badge>
                </td>
                <td className="px-4 py-3 text-right font-mono">
                  <span className={cn((adj.amount ?? 0) < 0 && 'text-red-500')}>
                    {formatCurrency(adj.amount)}
                  </span>
                </td>
                <td className="px-4 py-3 text-muted-foreground">{adj.reason || '—'}</td>
                <td className="px-4 py-3 text-muted-foreground">{formatDate(adj.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}

export function PayoutsPage() {
  const { data: payouts, isLoading } = usePayouts();

  const flatItems = payouts?.flatMap((p) =>
    p.items.map((item) => ({
      ...item,
      payoutDate: p.date,
      payoutStatus: p.status,
    }))
  ) ?? [];

  const totals = flatItems.reduce(
    (acc, item) => ({
      gross: acc.gross + (item.gross_amount ?? 0),
      fees: acc.fees + (item.fee_amount ?? 0),
      net: acc.net + (item.net_amount ?? 0),
    }),
    { gross: 0, fees: 0, net: 0 }
  );

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <h1 className="text-2xl font-bold">Payouts</h1>
        <div className="flex items-center gap-3">
          <PeriodFilter />
          <PeriodToggle />
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} height={48} baseColor="#1f2937" highlightColor="#374151" />
          ))}
        </div>
      ) : !flatItems.length ? (
        <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
          <p className="text-lg">No payout data</p>
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="px-4 py-2 text-left font-medium">Date</th>
                    <th className="px-4 py-2 text-left font-medium">Status</th>
                    <th className="px-4 py-2 text-right font-medium">Revenue</th>
                    <th className="px-4 py-2 text-right font-medium">Fees</th>
                    <th className="px-4 py-2 text-right font-medium">Net</th>
                  </tr>
                </thead>
                <tbody>
                  {flatItems.map((item, i) => (
                    <tr key={i} className="border-b">
                      <td className="px-4 py-3 text-muted-foreground">{formatDate(item.payoutDate)}</td>
                      <td className="px-4 py-3">
                        <Badge variant="outline" className="text-xs">{item.payoutStatus}</Badge>
                      </td>
                      <td className="px-4 py-3 text-right font-mono">{formatCurrency(item.gross_amount)}</td>
                      <td className="px-4 py-3 text-right font-mono text-red-500">
                        {(item.fee_amount ?? 0) > 0 ? `-${formatCurrency(item.fee_amount)}` : '—'}
                      </td>
                      <td className="px-4 py-3 text-right font-mono font-medium">{formatCurrency(item.net_amount)}</td>
                    </tr>
                  ))}
                  <tr className="border-t-2 font-bold">
                    <td className="px-4 py-3" colSpan={2}>Total</td>
                    <td className="px-4 py-3 text-right font-mono">{formatCurrency(totals.gross)}</td>
                    <td className="px-4 py-3 text-right font-mono text-red-500">-{formatCurrency(totals.fees)}</td>
                    <td className="px-4 py-3 text-right font-mono">{formatCurrency(totals.net)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      <AdjustmentsSection />
    </div>
  );
}
