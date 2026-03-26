export interface Order {
  id: string;
  order_number: string | null;
  customer_name: string | null;
  customer_email: string | null;
  status: string | null;
  financial_status: string | null;
  fulfillment_status: string | null;
  total_price: number | null;
  created_at: string | null;
}

export interface LineItem {
  id: string;
  title: string | null;
  sku: string | null;
  sku_cleaned: string | null;
  has_hidden_chars: boolean;
  variant_title: string | null;
  quantity: number;
  unit_price: number | null;
  total_price: number | null;
  discount_amount: number;
  tax_amount: number;
  fulfillment_status: string | null;
  refund_amount: number;
}

export interface OrderDetail extends Order {
  line_items: LineItem[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
}

export interface Store {
  id: string;
  name: string;
  shopify_domain: string | null;
  is_demo: boolean;
}

export interface Payout {
  id: string;
  date: string | null;
  amount: number | null;
  status: string | null;
  items: PayoutItem[];
}

export interface PayoutItem {
  line_item_id: string | null;
  gross_amount: number | null;
  fee_amount: number | null;
  net_amount: number | null;
}

export interface Adjustment {
  id: string;
  order_id: string | null;
  type: string | null;
  amount: number | null;
  reason: string | null;
  created_at: string | null;
}

export interface AnalyticsSummary {
  total_orders: number;
  revenue: number;
  average_order_value: number;
  refund_rate: number;
  fulfillment_rate: number;
  comparison?: Record<string, number | null>;
}

export interface ChartData {
  type: string;
  data: Record<string, unknown>[];
}

export interface ModeResponse {
  mode: string;
  connection_status: string;
  active_store: Store | null;
}

export interface TaskStatus {
  task_id: string;
  status: string;
  result?: unknown;
  meta?: { current: number; total: number };
}

export interface ApiError {
  message: string;
  code: string;
  detail: unknown;
}
