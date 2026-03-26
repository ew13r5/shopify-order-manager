import { useQuery, keepPreviousData } from '@tanstack/react-query';
import api from '@/lib/api';
import type { Order, OrderDetail, PaginatedResponse } from '@/types/api';

export interface OrderFilters {
  page: number;
  per_page: number;
  search?: string;
  status?: string;
  fulfillment_status?: string;
  sort_by?: string;
  sort_dir?: 'asc' | 'desc';
  date_from?: string;
  date_to?: string;
  sku?: string;
}

export function useOrders(filters: OrderFilters) {
  return useQuery<PaginatedResponse<Order>>({
    queryKey: ['orders', filters],
    queryFn: async () => {
      const params: Record<string, string | number> = {
        page: filters.page,
        per_page: filters.per_page,
      };
      if (filters.search) params.search = filters.search;
      if (filters.status) params.status = filters.status;
      if (filters.fulfillment_status) params.fulfillment_status = filters.fulfillment_status;
      if (filters.sort_by) params.sort_by = filters.sort_by;
      if (filters.sort_dir) params.sort_dir = filters.sort_dir;
      if (filters.date_from) params.date_from = filters.date_from;
      if (filters.date_to) params.date_to = filters.date_to;
      if (filters.sku) params.sku = filters.sku;
      const res = await api.get('/api/orders', { params });
      return res.data;
    },
    placeholderData: keepPreviousData,
  });
}

export function useOrderDetail(orderId: string | undefined) {
  return useQuery<OrderDetail>({
    queryKey: ['orders', orderId],
    queryFn: async () => {
      const res = await api.get(`/api/orders/${orderId}`);
      return res.data;
    },
    enabled: !!orderId,
  });
}
