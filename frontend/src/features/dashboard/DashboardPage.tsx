import { ShoppingCart, DollarSign, TrendingUp, Percent, Package } from 'lucide-react';
import { useSummary } from '@/hooks/useAnalytics';
import { formatCurrency } from '@/lib/utils';
import { PeriodFilter } from '@/components/shared/PeriodFilter';
import { MetricCard } from '@/components/shared/MetricCard';
import { RevenueChart } from './charts/RevenueChart';
import { TopProductsChart } from './charts/TopProductsChart';
import { OrderStatusChart } from './charts/OrderStatusChart';
import { PayoutTimelineChart } from './charts/PayoutTimelineChart';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';

function DashboardSkeleton() {
  return (
    <div className="space-y-6 p-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} height={120} baseColor="#1f2937" highlightColor="#374151" borderRadius={12} />
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} height={380} baseColor="#1f2937" highlightColor="#374151" borderRadius={12} />
        ))}
      </div>
    </div>
  );
}

export function DashboardPage() {
  const { data: summary, isLoading } = useSummary();

  if (isLoading) return <DashboardSkeleton />;

  const comparison = summary?.comparison;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <PeriodFilter />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Total Orders"
          value={summary?.total_orders?.toLocaleString() ?? '0'}
          change={comparison?.total_orders}
          icon={ShoppingCart}
        />
        <MetricCard
          title="Revenue"
          value={formatCurrency(summary?.revenue)}
          change={comparison?.revenue}
          icon={DollarSign}
        />
        <MetricCard
          title="Avg Order Value"
          value={formatCurrency(summary?.average_order_value)}
          change={comparison?.average_order_value}
          icon={TrendingUp}
        />
        <MetricCard
          title="Refund Rate"
          value={`${(summary?.refund_rate ?? 0).toFixed(1)}%`}
          change={comparison?.refund_rate}
          icon={Percent}
        />
        <MetricCard
          title="Fulfillment Rate"
          value={`${(summary?.fulfillment_rate ?? 0).toFixed(1)}%`}
          change={comparison?.fulfillment_rate}
          icon={Package}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <RevenueChart />
        <TopProductsChart />
        <OrderStatusChart />
        <PayoutTimelineChart />
      </div>
    </div>
  );
}
