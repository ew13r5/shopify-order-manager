import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useAppStore } from '@/stores/appStore';
import api from '@/lib/api';
import type { Store } from '@/types/api';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';

export function StoreSelector() {
  const { activeStoreId, setActiveStoreId } = useAppStore();

  const { data: stores = [] } = useQuery<Store[]>({
    queryKey: ['stores'],
    queryFn: async () => {
      const res = await api.get('/api/stores');
      return res.data;
    },
  });

  useEffect(() => {
    if (!activeStoreId && stores.length > 0) {
      setActiveStoreId(stores[0].id);
    }
  }, [activeStoreId, stores, setActiveStoreId]);

  if (stores.length === 0) return null;

  return (
    <Select
      value={activeStoreId || ''}
      onValueChange={(value) => setActiveStoreId(value)}
    >
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Select store" />
      </SelectTrigger>
      <SelectContent>
        {stores.map((store) => (
          <SelectItem key={store.id} value={store.id}>
            <div className="flex items-center gap-2">
              <span>{store.name}</span>
              <Badge variant={store.is_demo ? 'secondary' : 'default'} className="text-[10px] px-1.5 py-0">
                {store.is_demo ? 'Demo' : 'Live'}
              </Badge>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
