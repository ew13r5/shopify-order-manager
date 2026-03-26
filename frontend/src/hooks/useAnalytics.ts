import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import api from '@/lib/api';
import type { AnalyticsSummary, ChartData } from '@/types/api';

function useDateRange() {
  const [searchParams] = useSearchParams();
  const dateFrom = searchParams.get('date_from') || '';
  const dateTo = searchParams.get('date_to') || '';
  const period = searchParams.get('period') || '30d';
  return { dateFrom, dateTo, period };
}

export function useSummary() {
  const { dateFrom, dateTo, period } = useDateRange();

  return useQuery<AnalyticsSummary>({
    queryKey: ['analytics', 'summary', dateFrom, dateTo, period],
    queryFn: async () => {
      const params: Record<string, string> = { compare: 'true' };
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;
      if (!dateFrom && !dateTo) params.period = period;
      const res = await api.get('/api/analytics/summary', { params });
      return res.data;
    },
  });
}

export function useChartData(type: string) {
  const { dateFrom, dateTo, period } = useDateRange();

  return useQuery<ChartData>({
    queryKey: ['analytics', 'chart', type, dateFrom, dateTo, period],
    queryFn: async () => {
      const params: Record<string, string> = {};
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;
      if (!dateFrom && !dateTo) params.period = period;
      const res = await api.get(`/api/analytics/charts/${type}`, { params });
      return res.data;
    },
  });
}
