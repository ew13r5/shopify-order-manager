import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';
import { useAppStore } from '@/stores/appStore';
import api from '@/lib/api';
import type { TaskStatus } from '@/types/api';
import { toast } from 'sonner';

export function useSyncStatus(taskId: string | null) {
  return useQuery<TaskStatus>({
    queryKey: ['tasks', taskId],
    queryFn: async () => {
      const res = await api.get(`/api/tasks/${taskId}`);
      return res.data;
    },
    enabled: !!taskId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (!status) return 2500;
      if (['PENDING', 'STARTED', 'PROGRESS'].includes(status)) return 2500;
      return false;
    },
  });
}

export function useSync() {
  const [taskId, setTaskId] = useState<string | null>(null);
  const activeStoreId = useAppStore((s) => s.activeStoreId);

  const syncMutation = useMutation({
    mutationFn: async () => {
      if (!activeStoreId) throw new Error('No store selected');
      const res = await api.post(`/api/stores/${activeStoreId}/sync`);
      return res.data;
    },
    onSuccess: (data) => {
      setTaskId(data.task_id);
      toast.info('Sync started');
    },
    onError: () => {
      toast.error('Failed to start sync');
    },
  });

  const taskStatus = useSyncStatus(taskId);

  if (taskStatus.data?.status === 'SUCCESS' && taskId) {
    queryClient.invalidateQueries({ queryKey: ['orders'] });
    queryClient.invalidateQueries({ queryKey: ['payouts'] });
    queryClient.invalidateQueries({ queryKey: ['analytics'] });
    toast.success('Sync completed');
    setTaskId(null);
  }

  if (taskStatus.data?.status === 'FAILURE' && taskId) {
    toast.error('Sync failed');
    setTaskId(null);
  }

  return {
    startSync: () => syncMutation.mutate(),
    isSyncing: !!taskId || syncMutation.isPending,
    taskStatus: taskStatus.data,
    canSync: !!activeStoreId,
  };
}
