import { memo } from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useChartData } from '@/hooks/useAnalytics';

const STATUS_COLORS: Record<string, string> = {
  'Fulfilled': '#10b981',
  'Unfulfilled': '#f59e0b',
  'Partially Fulfilled': '#f97316',
  'fulfilled': '#10b981',
  'unfulfilled': '#f59e0b',
  'partial': '#f97316',
};

const DEFAULT_COLORS = ['#10b981', '#f59e0b', '#f97316', '#ef4444', '#6366f1'];

function ChartTooltip({ active, payload }: { active?: boolean; payload?: Array<{ name: string; value: number }> }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border bg-background p-2 shadow-md">
      <p className="text-xs text-muted-foreground">{payload[0].name}</p>
      <p className="text-sm font-bold">{payload[0].value.toLocaleString()} orders</p>
    </div>
  );
}

export const OrderStatusChart = memo(function OrderStatusChart() {
  const { data, isLoading } = useChartData('order_status');

  const chartData = (data?.data ?? []) as Array<{ status: string; count: number }>;
  const total = chartData.reduce((sum, d) => sum + d.count, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Order Status</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">Loading...</div>
        ) : !chartData.length ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">No data</div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="45%"
                innerRadius={60}
                outerRadius={100}
                dataKey="count"
                nameKey="status"
                paddingAngle={2}
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={index}
                    fill={STATUS_COLORS[entry.status] || DEFAULT_COLORS[index % DEFAULT_COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip content={<ChartTooltip />} />
              <Legend
                formatter={(value: string) => {
                  const item = chartData.find((d) => d.status === value);
                  const pct = item && total > 0 ? ((item.count / total) * 100).toFixed(0) : '0';
                  return <span className="text-xs text-muted-foreground">{value} ({pct}%)</span>;
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
});
