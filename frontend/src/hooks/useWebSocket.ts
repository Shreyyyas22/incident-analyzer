import { useEffect, useRef, useCallback } from 'react'
import { useStore } from '../store/useStore'

export function useWebSocket() {
  const ws = useRef<WebSocket | null>(null)
  const addLog = useStore(state => state.addLog)
  const setWsConnected = useStore(state => state.setWsConnected)
  const reconnectTimeout = useRef<number | null>(null)

  const connect = useCallback(() => {
    // In dev mode, we might need absolute URL if proxying is tricky
    // But since we set up proxy in vite.config, we can try relative
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host; // includes port
    const wsUrl = `${protocol}//${host}/ws/logs`;

    console.log(`Connecting to WebSocket: ${wsUrl}`);
    
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log('WebSocket Connected');
      setWsConnected(true);
      if (reconnectTimeout.current) {
        window.clearTimeout(reconnectTimeout.current);
        reconnectTimeout.current = null;
      }
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'log') {
          addLog(data.data);
        } else if (data.type === 'incident') {
          // We can handle new incidents here too if we want real-time incident notifications
          console.log('New Incident via WS:', data.data);
        }
      } catch (err) {
        console.error('Failed to parse WS message:', err);
      }
    };

    ws.current.onclose = () => {
      console.log('WebSocket Disconnected. Reconnecting...');
      setWsConnected(false);
      reconnectTimeout.current = window.setTimeout(connect, 3000);
    };

    ws.current.onerror = (err) => {
      console.error('WebSocket Error:', err);
      ws.current?.close();
    };
  }, [addLog, setWsConnected]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) window.clearTimeout(reconnectTimeout.current);
      ws.current?.close();
    };
  }, [connect]);

  return { isConnected: !!ws.current && ws.current.readyState === WebSocket.OPEN };
}
