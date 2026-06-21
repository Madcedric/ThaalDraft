import { useEffect, useState } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

interface SyncStatus {
  event: string;
  job_type: string;
  message?: string;
  error?: string;
}

export function useDocumentSync(documentId: string | null) {
  const [statusUpdates, setStatusUpdates] = useState<SyncStatus[]>([]);
  
  // Use WS_URL from env, default to standard local API port assuming ws instead of http
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const wsUrl = apiUrl.replace('http', 'ws') + `/ws/${documentId}`;

  const { lastMessage, readyState } = useWebSocket(
    documentId ? wsUrl : null,
    {
      shouldReconnect: (closeEvent) => true,
      reconnectAttempts: 10,
      reconnectInterval: 3000,
    }
  );

  useEffect(() => {
    if (lastMessage !== null) {
      try {
        const data = JSON.parse(lastMessage.data) as SyncStatus;
        setStatusUpdates(prev => [...prev, data]);
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

  return {
    connectionStatus,
    statusUpdates,
    latestUpdate: statusUpdates.length > 0 ? statusUpdates[statusUpdates.length - 1] : null
  };
}
