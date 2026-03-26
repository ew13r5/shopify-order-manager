import { memo } from 'react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useChartData } from '@/hooks/useAnalytics';

function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: Array<{ name: string; value: number; color: string }>; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg border bg-background p-2 shadow-md">
      <p className="text-xs text-muted-foreground mb-1">{label}</p>
      {payload.map((entry, i) => (
        <p key={i} className="text-xs" style={{ color: entry.color }}>
          {entry.name}: ${entry.value.toLocaleString()}
        </p>
      ))}
    </div>
  );
}

export const PayoutTimelineChart = memo(function PayoutTimelineChart() {
  const { data, isLoading } = useChartData('payout_timeline');

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Payout Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">Loading...</div>
        ) : !data?.data?.length ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">No data</div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.data}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(0 0% 20%)" />
              <XAxis dataKey="date" tick={{ fontSize: 12, fill: 'hsl(0 0% 60%)' }} />
              <YAxis tick={{ fontSize: 12, fill: 'hsl(0 0% 60%)' }} />
              <Tooltip content={<ChartTooltip />} />
              <Legend formatter={(value) => <span className="text-xs text-muted-foreground">{value}</span>} />
              <Bar dataKey="gross" stackId="a" fill="var(--color-chart-1)" radius={[0, 0, 0, 0]} />
              <Bar dataKey="fees" stackId="a" fill="var(--color-chart-5)" radius={[0, 0, 0, 0]} />
              <Bar dataKey="net" fill="var(--color-chart-2)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
});
