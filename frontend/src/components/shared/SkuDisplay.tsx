import { Badge } from '@/components/ui/badge';
import { AlertTriangle, Check } from 'lucide-react';

interface SkuDisplayProps {
  sku: string | null;
  skuCleaned: string | null;
  hasHiddenChars: boolean;
}

export function SkuDisplay({ sku, skuCleaned, hasHiddenChars }: SkuDisplayProps) {
  if (!sku) return <span className="text-muted-foreground">—</span>;

  if (!hasHiddenChars) {
    return <span className="font-mono text-sm">{sku}</span>;
  }

  return (
    <div className="space-y-1">
      <div className="flex items-center gap-1">
        <Badge variant="destructive" className="text-[10px] px-1 py-0 gap-1">
          <AlertTriangle className="h-3 w-3" />
          Unicode chars
        </Badge>
      </div>
      <div className="font-mono text-xs text-muted-foreground line-through">{sku}</div>
      <div className="flex items-center gap-1 font-mono text-sm">
        <Check className="h-3 w-3 text-emerald-500" />
        {skuCleaned}
      </div>
    </div>
  );
}
