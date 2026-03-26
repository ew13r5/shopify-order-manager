import { memo } from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useChartData } from '@/hooks/useAnalytics';

function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number }>; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border bg-background p-2 shadow-md">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-sm font-bold">{payload[0].value} sold</p>
    </div>
  );
}

export const TopProductsChart = memo(function TopProductsChart() {
  const { data, isLoading } = useChartData('top_products');

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Top Products</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">Loading...</div>
        ) : !data?.data?.length ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">No data</div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.data} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(0 0% 20%)" />
              <XAxis type="number" tick={{ fontSize: 12, fill: 'hsl(0 0% 60%)' }} />
              <YAxis dataKey="name" type="category" width={120} tick={{ fontSize: 11, fill: 'hsl(0 0% 60%)' }} />
              <Tooltip content={<ChartTooltip />} />
              <Bar dataKey="quantity" fill="var(--color-chart-2)" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
});
