import { useMutation } from '@tanstack/react-query';
import { useAppStore } from '@/stores/appStore';
import { queryClient } from '@/lib/queryClient';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

export function ModeSwitch() {
  const { currentMode, setCurrentMode, setActiveStoreId } = useAppStore();

  const mutation = useMutation({
    mutationFn: async (newMode: 'demo' | 'shopify') => {
      const res = await api.post('/api/mode', { mode: newMode });
      return res.data;
    },
    onSuccess: (_data, newMode) => {
      setCurrentMode(newMode);
      setActiveStoreId(null);
      queryClient.invalidateQueries();
      toast.success(`Switched to ${newMode === 'demo' ? 'Demo' : 'Live'} mode`);
    },
    onError: () => {
      toast.error('Failed to switch mode');
    },
  });

  const nextMode = currentMode === 'demo' ? 'shopify' : 'demo';

  return (
    <div className="flex items-center gap-2">
      <Badge variant={currentMode === 'demo' ? 'secondary' : 'default'}>
        {currentMode === 'demo' ? 'Demo' : 'Live'}
      </Badge>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => mutation.mutate(nextMode)}
        disabled={mutation.isPending}
      >
        {mutation.isPending ? 'Switching...' : `Switch to ${nextMode === 'demo' ? 'Demo' : 'Live'}`}
      </Button>
    </div>
  );
}
