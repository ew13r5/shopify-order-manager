import { useQuery, keepPreviousData } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import api from '@/lib/api';
import type { Adjustment } from '@/types/api';

export interface PayoutFilters {
  page: number;
  per_page: number;
  search?: string;
}

export interface PayoutItemRow {
  id: string;
  payout_date: string | null;
  payout_status: string | null;
  order_number: string | null;
  product: string | null;
  sku: string | null;
  quantity: number;
  gross_amount: number;
  fee_amount: number;
  discount_amount: number;
  refund_amount: number;
  net_amount: number;
}

export interface PayoutsPaginatedResponse {
  items: PayoutItemRow[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  totals: {
    gross: number;
    fees: number;
    net: number;
  };
}

export function usePayouts(filters: PayoutFilters) {
  return useQuery<PayoutsPaginatedResponse>({
    queryKey: ['payouts', filters],
    queryFn: async () => {
      const params: Record<string, string | number> = {
        page: filters.page,
        per_page: filters.per_page,
      };
      if (filters.search) params.search = filters.search;
      const res = await api.get('/api/payouts', { params });
      return res.data;
    },
    placeholderData: keepPreviousData,
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
