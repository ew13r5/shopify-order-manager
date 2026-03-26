import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import api from '@/lib/api';
import { useSyncStatus } from '@/hooks/useSync';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Download, FileSpreadsheet, Sheet, ExternalLink, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'sonner';

type ExportType = 'orders' | 'items' | 'payouts';

interface ExportPanelProps {
  dateFrom?: string;
  dateTo?: string;
}

function SheetsProgress({ taskId, onDismiss }: { taskId: string; onDismiss: () => void }) {
  const { data: taskStatus } = useSyncStatus(taskId);

  const status = taskStatus?.status;
  const progress = taskStatus?.meta
    ? Math.round((taskStatus.meta.current / taskStatus.meta.total) * 100)
    : null;

  if (status === 'SUCCESS') {
    const url = taskStatus?.result as string | undefined;
    return (
      <div className="flex items-center gap-2 p-3 rounded-md bg-emerald-500/10 border border-emerald-500/30">
        <CheckCircle className="h-4 w-4 text-emerald-500" />
        <span className="text-sm flex-1">Export complete</span>
        {url && (
          <a href={url} target="_blank" rel="noopener noreferrer" className="text-sm text-emerald-400 hover:underline flex items-center gap-1">
            Open Sheet <ExternalLink className="h-3 w-3" />
          </a>
        )}
        <Button variant="ghost" size="sm" onClick={onDismiss} className="text-xs">Dismiss</Button>
      </div>
    );
  }

  if (status === 'FAILURE') {
    return (
      <div className="flex items-center gap-2 p-3 rounded-md bg-red-500/10 border border-red-500/30">
        <XCircle className="h-4 w-4 text-red-500" />
        <span className="text-sm flex-1">Export failed</span>
        <Button variant="ghost" size="sm" onClick={onDismiss} className="text-xs">Dismiss</Button>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div
          className="h-full bg-primary transition-all duration-300 rounded-full"
          style={{ width: progress != null ? `${progress}%` : '30%' }}
        />
      </div>
      <p className="text-xs text-muted-foreground">
        {progress != null && taskStatus?.meta
          ? `Exporting sheet ${taskStatus.meta.current}/${taskStatus.meta.total}...`
          : 'Preparing export...'}
      </p>
    </div>
  );
}

export function ExportPanel({ dateFrom, dateTo }: ExportPanelProps) {
  const [exportType, setExportType] = useState<ExportType>('orders');
  const [sheetsTaskId, setSheetsTaskId] = useState<string | null>(null);

  const baseUrl = import.meta.env.VITE_API_URL || '';

  function downloadCsv() {
    const params = new URLSearchParams({ type: exportType });
    if (dateFrom) params.set('date_from', dateFrom);
    if (dateTo) params.set('date_to', dateTo);
    window.open(`${baseUrl}/api/export/csv?${params}`, '_blank');
  }

  function downloadExcel() {
    const params = new URLSearchParams({ type: exportType });
    if (dateFrom) params.set('date_from', dateFrom);
    if (dateTo) params.set('date_to', dateTo);
    window.open(`${baseUrl}/api/export/xlsx?${params}`, '_blank');
  }

  const sheetsMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post('/api/export/gsheets', {
        type: exportType,
        date_from: dateFrom,
        date_to: dateTo,
      });
      return res.data;
    },
    onSuccess: (data) => {
      setSheetsTaskId(data.task_id);
      toast.info('Google Sheets export started');
    },
    onError: () => {
      toast.error('Failed to start export');
    },
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm">Export</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-3 flex-wrap">
          <Select value={exportType} onValueChange={(v) => setExportType(v as ExportType)}>
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="orders">Orders</SelectItem>
              <SelectItem value="items">Line Items</SelectItem>
              <SelectItem value="payouts">Payouts</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="outline" size="sm" onClick={downloadCsv}>
            <Download className="h-3 w-3 mr-1" /> CSV
          </Button>
          <Button variant="outline" size="sm" onClick={downloadExcel}>
            <FileSpreadsheet className="h-3 w-3 mr-1" /> Excel
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => sheetsMutation.mutate()}
            disabled={!!sheetsTaskId || sheetsMutation.isPending}
          >
            {sheetsMutation.isPending ? (
              <Loader2 className="h-3 w-3 animate-spin mr-1" />
            ) : (
              <Sheet className="h-3 w-3 mr-1" />
            )}
            Google Sheets
          </Button>
        </div>

        {sheetsTaskId && (
          <SheetsProgress
            taskId={sheetsTaskId}
            onDismiss={() => setSheetsTaskId(null)}
          />
        )}
      </CardContent>
    </Card>
  );
}
