import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import api from '@/lib/api';
import type { Payout, Adjustment } from '@/types/api';

export function usePayouts() {
  const [searchParams] = useSearchParams();
  const dateFrom = searchParams.get('date_from') || '';
  const dateTo = searchParams.get('date_to') || '';
  const period = searchParams.get('period') || '30d';

  return useQuery<Payout[]>({
    queryKey: ['payouts', { dateFrom, dateTo, period }],
    queryFn: async () => {
      const params: Record<string, string> = {};
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;
      if (!dateFrom && !dateTo) params.period = period;
      const res = await api.get('/api/payouts', { params });
      return res.data;
    },
  });
}

export function useAdjustments() {
  const [searchParams] = useSearchParams();
  const dateFrom = searchParams.get('date_from') || '';
  const dateTo = searchParams.get('date_to') || '';

  return useQuery<Adjustment[]>({
    queryKey: ['adjustments', { dateFrom, dateTo }],
    queryFn: async () => {
      const params: Record<string, string> = {};
      if (dateFrom) params.date_from = dateFrom;
      if (dateTo) params.date_to = dateTo;
      const res = await api.get('/api/adjustments', { params });
      return res.data;
    },
  });
}
