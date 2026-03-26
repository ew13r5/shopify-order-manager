import { useParams, useNavigate } from 'react-router-dom';
import { useOrderDetail } from '@/hooks/useOrders';
import { formatCurrency, formatDate } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SkuDisplay } from '@/components/shared/SkuDisplay';
import { ArrowLeft } from 'lucide-react';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';

function statusBadgeVariant(status: string | null) {
  switch (status) {
    case 'paid': case 'closed': return 'default' as const;
    case 'pending': return 'secondary' as const;
    case 'refunded': case 'cancelled': return 'destructive' as const;
    default: return 'outline' as const;
  }
}

export function OrderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: order, isLoading, isError } = useOrderDetail(id);

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <Skeleton height={40} width={200} baseColor="#1f2937" highlightColor="#374151" />
        <Skeleton height={200} baseColor="#1f2937" highlightColor="#374151" borderRadius={12} />
        <Skeleton height={300} baseColor="#1f2937" highlightColor="#374151" borderRadius={12} />
      </div>
    );
  }

  if (isError || !order) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
        <p className="text-lg">Order not found</p>
        <Button variant="ghost" className="mt-4" onClick={() => navigate('/orders')}>
          <ArrowLeft className="h-4 w-4 mr-2" /> Back to Orders
        </Button>
      </div>
    );
  }

  const subtotal = order.line_items.reduce((sum, li) => sum + (li.total_price ?? 0), 0);
  const totalDiscount = order.line_items.reduce((sum, li) => sum + li.discount_amount, 0);
  const totalTax = order.line_items.reduce((sum, li) => sum + li.tax_amount, 0);
  const totalRefund = order.line_items.reduce((sum, li) => sum + li.refund_amount, 0);

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/orders')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Order #{order.order_number}</h1>
          <p className="text-sm text-muted-foreground">{formatDate(order.created_at)}</p>
        </div>
        <div className="flex gap-2 ml-auto">
          <Badge variant={statusBadgeVariant(order.financial_status)}>
            {order.financial_status || 'unknown'}
          </Badge>
          {order.fulfillment_status && (
            <Badge variant="outline">{order.fulfillment_status}</Badge>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm">Line Items</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="px-4 py-2 text-left font-medium">Product</th>
                    <th className="px-4 py-2 text-left font-medium">SKU</th>
                    <th className="px-4 py-2 text-left font-medium">Variant</th>
                    <th className="px-4 py-2 text-center font-medium">Qty</th>
                    <th className="px-4 py-2 text-right font-medium">Unit Price</th>
                    <th className="px-4 py-2 text-right font-medium">Total</th>
                    <th className="px-4 py-2 text-right font-medium">Discount</th>
                    <th className="px-4 py-2 text-right font-medium">Tax</th>
                    <th className="px-4 py-2 text-left font-medium">Status</th>
                    <th className="px-4 py-2 text-right font-medium">Refund</th>
                  </tr>
                </thead>
                <tbody>
                  {order.line_items.map((item) => (
                    <tr key={item.id} className="border-b">
                      <td className="px-4 py-3">{item.title || '—'}</td>
                      <td className="px-4 py-3">
                        <SkuDisplay
                          sku={item.sku}
                          skuCleaned={item.sku_cleaned}
                          hasHiddenChars={item.has_hidden_chars}
                        />
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">{item.variant_title || '—'}</td>
                      <td className="px-4 py-3 text-center">{item.quantity}</td>
                      <td className="px-4 py-3 text-right">{formatCurrency(item.unit_price)}</td>
                      <td className="px-4 py-3 text-right">{formatCurrency(item.total_price)}</td>
                      <td className="px-4 py-3 text-right">{item.discount_amount > 0 ? `-${formatCurrency(item.discount_amount)}` : '—'}</td>
                      <td className="px-4 py-3 text-right">{item.tax_amount > 0 ? formatCurrency(item.tax_amount) : '—'}</td>
                      <td className="px-4 py-3">
                        {item.fulfillment_status && (
                          <Badge variant="outline" className="text-xs">{item.fulfillment_status}</Badge>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right">
                        {item.refund_amount > 0 ? (
                          <span className="text-red-500">{formatCurrency(item.refund_amount)}</span>
                        ) : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Customer</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="font-medium">{order.customer_name || 'Guest'}</p>
              {order.customer_email && (
                <p className="text-sm text-muted-foreground mt-1">{order.customer_email}</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Order Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Subtotal</span>
                <span>{formatCurrency(subtotal)}</span>
              </div>
              {totalDiscount > 0 && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Discounts</span>
                  <span className="text-red-500">-{formatCurrency(totalDiscount)}</span>
                </div>
              )}
              {totalTax > 0 && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Tax</span>
                  <span>{formatCurrency(totalTax)}</span>
                </div>
              )}
              <div className="border-t pt-2 flex justify-between font-bold">
                <span>Total</span>
                <span>{formatCurrency(order.total_price)}</span>
              </div>
              {totalRefund > 0 && (
                <div className="flex justify-between text-red-500">
                  <span>Refunded</span>
                  <span>{formatCurrency(totalRefund)}</span>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
