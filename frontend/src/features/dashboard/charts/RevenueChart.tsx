import { memo } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useChartData } from '@/hooks/useAnalytics';

function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ value: number }>; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border bg-background p-2 shadow-md">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-sm font-bold">${payload[0].value.toLocaleString()}</p>
    </div>
  );
}

export const RevenueChart = memo(function RevenueChart() {
  const { data, isLoading } = useChartData('revenue');

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Revenue Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">Loading...</div>
        ) : !data?.data?.length ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">No data</div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.data}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(0 0% 20%)" />
              <XAxis dataKey="date" tick={{ fontSize: 12, fill: 'hsl(0 0% 60%)' }} />
              <YAxis tick={{ fontSize: 12, fill: 'hsl(0 0% 60%)' }} />
              <Tooltip content={<ChartTooltip />} />
              <Line type="monotone" dataKey="revenue" stroke="var(--color-chart-1)" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
});
