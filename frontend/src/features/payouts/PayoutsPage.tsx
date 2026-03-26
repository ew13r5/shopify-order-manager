import { useState, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { usePayouts, type PayoutFilters } from '@/hooks/usePayouts';
import { useDebounce } from '@/hooks/useDebounce';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { MetricCard } from '@/components/shared/MetricCard';
import { ChevronLeft, ChevronRight, Search, DollarSign, TrendingDown, Wallet } from 'lucide-react';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';

export function PayoutsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchInput, setSearchInput] = useState(searchParams.get('search') || '');
  const debouncedSearch = useDebounce(searchInput, 300);

  const filters: PayoutFilters = useMemo(() => ({
    page: Number(searchParams.get('page')) || 1,
    per_page: 20,
    search: debouncedSearch || undefined,
  }), [searchParams, debouncedSearch]);

  const { data, isLoading } = usePayouts(filters);

  function updateParams(updates: Record<string, string | undefined>) {
    const next = new URLSearchParams(searchParams);
    for (const [key, value] of Object.entries(updates)) {
      if (value) next.set(key, value);
      else next.delete(key);
    }
    if (!('page' in updates)) next.set('page', '1');
    setSearchParams(next, { replace: true });
  }

  const currentPage = data?.page ?? 1;
  const totalPages = data ? Math.ceil(data.total / data.per_page) : 0;

  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Payout Breakdown</h1>

      {/* Summary cards */}
      {data?.totals && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <MetricCard
            title="Gross Revenue"
            value={formatCurrency(data.totals.gross)}
            icon={DollarSign}
          />
          <MetricCard
            title="Total Fees"
            value={`-${formatCurrency(data.totals.fees)}`}
            icon={TrendingDown}
          />
          <MetricCard
            title="Net Payouts"
            value={formatCurrency(data.totals.net)}
            icon={Wallet}
          />
        </div>
      )}

      {/* Search */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by product, SKU, order #..."
            value={searchInput}
            onChange={(e) => {
              setSearchInput(e.target.value);
              updateParams({ search: e.target.value || undefined, page: '1' });
            }}
            className="w-full rounded-md border border-input bg-background px-9 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 10 }).map((_, i) => (
            <Skeleton key={i} height={48} baseColor="#1f2937" highlightColor="#374151" />
          ))}
        </div>
      ) : !data?.items?.length ? (
        <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
          <p className="text-lg">No payout data</p>
        </div>
      ) : (
        <>
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="px-4 py-2 text-left font-medium">Product</th>
                      <th className="px-4 py-2 text-left font-medium">SKU</th>
                      <th className="px-4 py-2 text-left font-medium">Order</th>
                      <th className="px-4 py-2 text-center font-medium">Qty</th>
                      <th className="px-4 py-2 text-right font-medium">Gross</th>
                      <th className="px-4 py-2 text-right font-medium">Fees</th>
                      <th className="px-4 py-2 text-right font-medium">Discounts</th>
                      <th className="px-4 py-2 text-right font-medium">Refunds</th>
                      <th className="px-4 py-2 text-right font-medium">Net Payout</th>
                      <th className="px-4 py-2 text-left font-medium">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.items.map((item) => (
                      <tr key={item.id} className="border-b hover:bg-muted/30 transition-colors">
                        <td className="px-4 py-3 max-w-[200px] truncate">{item.product || '—'}</td>
                        <td className="px-4 py-3 font-mono text-xs">{item.sku || '—'}</td>
                        <td className="px-4 py-3 text-muted-foreground">#{item.order_number}</td>
                        <td className="px-4 py-3 text-center">{item.quantity}</td>
                        <td className="px-4 py-3 text-right font-mono">{formatCurrency(item.gross_amount)}</td>
                        <td className="px-4 py-3 text-right font-mono text-red-400">
                          {item.fee_amount > 0 ? `-${formatCurrency(item.fee_amount)}` : '—'}
                        </td>
                        <td className="px-4 py-3 text-right font-mono text-red-400">
                          {item.discount_amount > 0 ? `-${formatCurrency(item.discount_amount)}` : '—'}
                        </td>
                        <td className="px-4 py-3 text-right font-mono text-red-400">
                          {item.refund_amount > 0 ? `-${formatCurrency(item.refund_amount)}` : '—'}
                        </td>
                        <td className="px-4 py-3 text-right font-mono font-medium text-emerald-400">
                          {formatCurrency(item.net_amount)}
                        </td>
                        <td className="px-4 py-3 text-muted-foreground text-xs">{formatDate(item.payout_date)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">
              Page {currentPage} of {totalPages} — {data.total.toLocaleString()} payout items
            </span>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={data.page <= 1}
                onClick={() => updateParams({ page: String(data.page - 1) })}
              >
                <ChevronLeft className="h-4 w-4" /> Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={!data.has_next}
                onClick={() => updateParams({ page: String(data.page + 1) })}
              >
                Next <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
