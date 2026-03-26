import { useState, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useOrders, type OrderFilters } from '@/hooks/useOrders';
import { useDebounce } from '@/hooks/useDebounce';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ChevronLeft, ChevronRight, Search, X } from 'lucide-react';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';

const FINANCIAL_STATUS_OPTIONS = [
  { value: 'all', label: 'All statuses' },
  { value: 'paid', label: 'Paid' },
  { value: 'partially_refunded', label: 'Partially Refunded' },
  { value: 'refunded', label: 'Refunded' },
  { value: 'pending', label: 'Pending' },
] as const;

const FULFILLMENT_OPTIONS = [
  { value: 'all', label: 'All fulfillment' },
  { value: 'fulfilled', label: 'Fulfilled' },
  { value: 'unfulfilled', label: 'Unfulfilled' },
  { value: 'partial', label: 'Partial' },
] as const;

function financialBadge(status: string | null) {
  switch (status) {
    case 'paid':
      return <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/15">Paid</Badge>;
    case 'partially_refunded':
      return <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 hover:bg-amber-500/15">Partially Refunded</Badge>;
    case 'refunded':
      return <Badge className="bg-red-500/15 text-red-400 border-red-500/30 hover:bg-red-500/15">Refunded</Badge>;
    case 'pending':
      return <Badge className="bg-zinc-500/15 text-zinc-400 border-zinc-500/30 hover:bg-zinc-500/15">Pending</Badge>;
    default:
      return <Badge variant="outline">{status || 'Unknown'}</Badge>;
  }
}

function fulfillmentBadge(status: string | null) {
  switch (status) {
    case 'fulfilled':
      return <Badge className="bg-emerald-500/15 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/15">Fulfilled</Badge>;
    case 'unfulfilled':
      return <Badge className="bg-amber-500/15 text-amber-400 border-amber-500/30 hover:bg-amber-500/15">Unfulfilled</Badge>;
    case 'partial':
      return <Badge className="bg-orange-500/15 text-orange-400 border-orange-500/30 hover:bg-orange-500/15">Partial</Badge>;
    default:
      return <Badge variant="outline">{status || '—'}</Badge>;
  }
}

export function OrdersPage() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [searchInput, setSearchInput] = useState(searchParams.get('search') || '');
  const debouncedSearch = useDebounce(searchInput, 300);

  const filters: OrderFilters = useMemo(() => ({
    page: Number(searchParams.get('page')) || 1,
    per_page: 20,
    search: debouncedSearch || undefined,
    status: searchParams.get('status') || undefined,
    fulfillment_status: searchParams.get('fulfillment_status') || undefined,
    sort_by: searchParams.get('sort_by') || undefined,
    sort_dir: (searchParams.get('sort_dir') as 'asc' | 'desc') || undefined,
  }), [searchParams, debouncedSearch]);

  const { data, isLoading } = useOrders(filters);

  function updateParams(updates: Record<string, string | undefined>) {
    const next = new URLSearchParams(searchParams);
    for (const [key, value] of Object.entries(updates)) {
      if (value) next.set(key, value);
      else next.delete(key);
    }
    if (updates.page === undefined && !('page' in updates)) {
      next.set('page', '1');
    }
    setSearchParams(next, { replace: true });
  }

  function toggleSort(column: string) {
    const currentSort = searchParams.get('sort_by');
    const currentDir = searchParams.get('sort_dir');
    if (currentSort === column && currentDir === 'asc') {
      updateParams({ sort_by: column, sort_dir: 'desc', page: '1' });
    } else if (currentSort === column && currentDir === 'desc') {
      updateParams({ sort_by: undefined, sort_dir: undefined, page: '1' });
    } else {
      updateParams({ sort_by: column, sort_dir: 'asc', page: '1' });
    }
  }

  function getSortIndicator(column: string) {
    if (searchParams.get('sort_by') !== column) return '';
    return searchParams.get('sort_dir') === 'asc' ? ' ↑' : ' ↓';
  }

  function clearFilters() {
    setSearchInput('');
    setSearchParams({}, { replace: true });
  }

  const hasFilters = searchParams.get('search') || searchParams.get('status') || searchParams.get('fulfillment_status');

  const currentPage = data?.page ?? 1;
  const totalPages = data ? Math.ceil(data.total / data.per_page) : 0;

  return (
    <div className="space-y-4 p-6">
      <h1 className="text-2xl font-bold">Orders</h1>

      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by order #, customer, SKU..."
            value={searchInput}
            onChange={(e) => {
              setSearchInput(e.target.value);
              updateParams({ search: e.target.value || undefined, page: '1' });
            }}
            className="w-full rounded-md border border-input bg-background px-9 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>

        <Select
          value={searchParams.get('status') || 'all'}
          onValueChange={(value) => updateParams({ status: value === 'all' ? undefined : value, page: '1' })}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            {FINANCIAL_STATUS_OPTIONS.map((s) => (
              <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select
          value={searchParams.get('fulfillment_status') || 'all'}
          onValueChange={(value) => updateParams({ fulfillment_status: value === 'all' ? undefined : value, page: '1' })}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Fulfillment" />
          </SelectTrigger>
          <SelectContent>
            {FULFILLMENT_OPTIONS.map((s) => (
              <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            <X className="h-4 w-4 mr-1" /> Clear
          </Button>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 10 }).map((_, i) => (
            <Skeleton key={i} height={48} baseColor="#1f2937" highlightColor="#374151" />
          ))}
        </div>
      ) : !data?.items?.length ? (
        <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
          <p className="text-lg">No orders found</p>
          {hasFilters && <p className="text-sm mt-1">Try adjusting your filters</p>}
        </div>
      ) : (
        <>
          <div className="rounded-md border">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-muted/50">
                  <th className="px-4 py-3 text-left font-medium cursor-pointer hover:text-foreground" onClick={() => toggleSort('order_number')}>
                    Order #{getSortIndicator('order_number')}
                  </th>
                  <th className="px-4 py-3 text-left font-medium cursor-pointer hover:text-foreground" onClick={() => toggleSort('created_at')}>
                    Date{getSortIndicator('created_at')}
                  </th>
                  <th className="px-4 py-3 text-left font-medium">Customer</th>
                  <th className="px-4 py-3 text-left font-medium">Status</th>
                  <th className="px-4 py-3 text-center font-medium">Items</th>
                  <th className="px-4 py-3 text-right font-medium cursor-pointer hover:text-foreground" onClick={() => toggleSort('total_price')}>
                    Total{getSortIndicator('total_price')}
                  </th>
                  <th className="px-4 py-3 text-left font-medium">Fulfillment</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((order) => (
                  <tr
                    key={order.id}
                    className="border-b cursor-pointer hover:bg-muted/30 transition-colors"
                    onClick={() => navigate(`/orders/${order.id}`)}
                  >
                    <td className="px-4 py-3 font-medium">#{order.order_number}</td>
                    <td className="px-4 py-3 text-muted-foreground">{formatDate(order.created_at)}</td>
                    <td className="px-4 py-3">{order.customer_name || '—'}</td>
                    <td className="px-4 py-3">{financialBadge(order.financial_status)}</td>
                    <td className="px-4 py-3 text-center text-muted-foreground">{order.items_count}</td>
                    <td className="px-4 py-3 text-right font-medium">{formatCurrency(order.total_price)}</td>
                    <td className="px-4 py-3">{fulfillmentBadge(order.fulfillment_status)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">
              Page {currentPage} of {totalPages} — {data.total.toLocaleString()} orders
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
