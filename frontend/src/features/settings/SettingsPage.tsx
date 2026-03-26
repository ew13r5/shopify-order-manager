import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useAppStore } from '@/stores/appStore';
import { queryClient } from '@/lib/queryClient';
import api from '@/lib/api';
import { useSync } from '@/hooks/useSync';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RefreshCw, ExternalLink, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

function ModeSettings() {
  const { currentMode, setCurrentMode, setActiveStoreId } = useAppStore();

  const modeMutation = useMutation({
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
  });

  const resetMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post('/api/demo/reset');
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries();
      toast.success('Demo data reset');
    },
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Mode</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">Current Mode</p>
            <Badge variant={currentMode === 'demo' ? 'secondary' : 'default'} className="mt-1">
              {currentMode === 'demo' ? 'Demo' : 'Live'}
            </Badge>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => modeMutation.mutate(currentMode === 'demo' ? 'shopify' : 'demo')}
            disabled={modeMutation.isPending}
          >
            Switch to {currentMode === 'demo' ? 'Live' : 'Demo'}
          </Button>
        </div>
        {currentMode === 'demo' && (
          <Button
            variant="secondary"
            size="sm"
            onClick={() => resetMutation.mutate()}
            disabled={resetMutation.isPending}
          >
            <RefreshCw className={`h-3 w-3 mr-1 ${resetMutation.isPending ? 'animate-spin' : ''}`} />
            Reset Demo Data
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

function StoreConnect() {
  const [storeUrl, setStoreUrl] = useState('');
  const [accessToken, setAccessToken] = useState('');

  const tokenMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post('/api/auth/shopify/token', {
        store_url: storeUrl,
        access_token: accessToken,
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stores'] });
      toast.success('Store connected');
      setStoreUrl('');
      setAccessToken('');
    },
    onError: () => {
      toast.error('Failed to connect store');
    },
  });

  const oauthMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post('/api/auth/shopify/connect', { store_url: storeUrl });
      return res.data;
    },
    onSuccess: (data) => {
      window.location.href = data.auth_url;
    },
    onError: () => {
      toast.error('Failed to start OAuth');
    },
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Connect Store</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div>
            <label className="text-sm font-medium mb-1 block">Store URL</label>
            <input
              type="text"
              placeholder="mystore.myshopify.com"
              value={storeUrl}
              onChange={(e) => setStoreUrl(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Access Token (Custom App)</label>
            <input
              type="password"
              placeholder="shpat_..."
              value={accessToken}
              onChange={(e) => setAccessToken(e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
            />
          </div>
          <div className="flex gap-2">
            <Button
              size="sm"
              onClick={() => tokenMutation.mutate()}
              disabled={!storeUrl || !accessToken || tokenMutation.isPending}
            >
              {tokenMutation.isPending && <Loader2 className="h-3 w-3 animate-spin mr-1" />}
              Connect with Token
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => oauthMutation.mutate()}
              disabled={!storeUrl || oauthMutation.isPending}
            >
              <ExternalLink className="h-3 w-3 mr-1" />
              OAuth Connect
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function SyncPanel() {
  const { startSync, isSyncing, canSync, taskStatus } = useSync();

  const progress = taskStatus?.meta
    ? Math.round((taskStatus.meta.current / taskStatus.meta.total) * 100)
    : null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Sync</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Sync orders and payouts from Shopify
          </p>
          <Button
            size="sm"
            onClick={startSync}
            disabled={!canSync || isSyncing}
          >
            {isSyncing && <Loader2 className="h-3 w-3 animate-spin mr-1" />}
            {isSyncing ? 'Syncing...' : 'Sync Now'}
          </Button>
        </div>
        {isSyncing && (
          <div className="space-y-2">
            <div className="h-2 rounded-full bg-muted overflow-hidden">
              <div
                className="h-full bg-primary transition-all duration-300 rounded-full"
                style={{ width: progress != null ? `${progress}%` : '30%' }}
              />
            </div>
            <p className="text-xs text-muted-foreground">
              {progress != null
                ? `${progress}% — ${taskStatus?.meta?.current}/${taskStatus?.meta?.total}`
                : 'Starting sync...'}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function SettingsPage() {
  return (
    <div className="space-y-6 p-6">
      <h1 className="text-2xl font-bold">Settings</h1>
      <div className="space-y-4 max-w-2xl">
        <ModeSettings />
        <StoreConnect />
        <SyncPanel />
      </div>
    </div>
  );
}
