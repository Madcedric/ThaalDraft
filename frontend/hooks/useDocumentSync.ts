import { useEffect, useState, useCallback } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

export interface ReconstructionStep {
  step: string;
  status: 'running' | 'completed' | 'failed' | 'skipped';
  message?: string;
}

interface SyncStatus {
  event: string;
  job_type?: string;
  step?: string;
  status?: string;
  message?: string;
  error?: string;
  results?: Record<string, unknown>;
}

export interface DocumentSyncReturn {
  connectionStatus: string;
  statusUpdates: SyncStatus[];
  latestUpdate: SyncStatus | null;
  reconstructionSteps: ReconstructionStep[];
  reconstructionProgress: number;
  isReconstructing: boolean;
}

export function useDocumentSync(documentId: string | null): DocumentSyncReturn {
  const [statusUpdates, setStatusUpdates] = useState<SyncStatus[]>([]);
  const [reconstructionSteps, setReconstructionSteps] = useState<ReconstructionStep[]>([]);

  const apiUrl = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';
  const wsUrl = apiUrl.replace('http', 'ws') + `/ws/${documentId}`;

  const { lastMessage, readyState } = useWebSocket(
    documentId ? wsUrl : null,
    {
      shouldReconnect: () => true,
      reconnectAttempts: 10,
      reconnectInterval: 3000,
    }
  );

  useEffect(() => {
    if (lastMessage !== null) {
      try {
        const data = JSON.parse(lastMessage.data) as SyncStatus;
        setStatusUpdates(prev => [...prev, data]);

        if (data.event === 'reconstruction_progress' && data.step && data.status) {
          setReconstructionSteps(prev => {
            const existing = prev.findIndex(s => s.step === data.step);
            const step: ReconstructionStep = {
              step: data.step!,
              status: data.status as ReconstructionStep['status'],
              message: data.message,
            };
            if (existing >= 0) {
              const next = [...prev];
              next[existing] = step;
              return next;
            }
            return [...prev, step];
          });
        }

        if (data.event === 'job_completed' && data.job_type === 'reconstruction') {
          setReconstructionSteps([]);
        }
      } catch (e) {
        console.error("Failed to parse websocket message", e);
      }
    }
  }, [lastMessage]);

  const connectionStatus = {
    [ReadyState.CONNECTING]: 'Connecting',
    [ReadyState.OPEN]: 'Open',
    [ReadyState.CLOSING]: 'Closing',
    [ReadyState.CLOSED]: 'Closed',
    [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
  }[readyState];

  const stepOrder = ['parse', 'structure', 'citations', 'compliance', 'review'];
  const completedSteps = reconstructionSteps.filter(s => s.status === 'completed' || s.status === 'skipped').length;
  const failedSteps = reconstructionSteps.filter(s => s.status === 'failed').length;
  const reconstructionProgress = Math.round(((completedSteps + failedSteps) / stepOrder.length) * 100);
  const isReconstructing = reconstructionSteps.some(s => s.status === 'running') ||
    (reconstructionSteps.length > 0 && completedSteps + failedSteps < stepOrder.length);

  return {
    connectionStatus,
    statusUpdates,
    latestUpdate: statusUpdates.length > 0 ? statusUpdates[statusUpdates.length - 1] : null,
    reconstructionSteps,
    reconstructionProgress,
    isReconstructing,
  };
}
