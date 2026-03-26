import { useMutation } from '@tanstack/react-query';
import { useAppStore } from '@/stores/appStore';
import { queryClient } from '@/lib/queryClient';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

export function DemoBanner() {
  const currentMode = useAppStore((s) => s.currentMode);

  const resetMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post('/api/demo/reset');
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries();
      toast.success('Demo data has been reset');
    },
    onError: () => {
      toast.error('Failed to reset demo data');
    },
  });

  if (currentMode !== 'demo') return null;

  return (
    <div className="flex items-center justify-between gap-4 border-b border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm text-amber-400">
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-4 w-4" />
        <span>You are viewing demo data. Connect a Shopify store for real data.</span>
      </div>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => resetMutation.mutate()}
        disabled={resetMutation.isPending}
        className="text-amber-400 hover:text-amber-300"
      >
        <RefreshCw className={`h-3 w-3 mr-1 ${resetMutation.isPending ? 'animate-spin' : ''}`} />
        {resetMutation.isPending ? 'Resetting...' : 'Reset Demo Data'}
      </Button>
    </div>
  );
}
