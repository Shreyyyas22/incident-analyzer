import { useStore, LogEntry } from '../store/useStore';
import { format } from 'date-fns';

export function LogsPage() {
  const logs = useStore(state => state.logs);

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR':
      case 'CRITICAL': return 'var(--error)';
      case 'WARNING': return 'var(--warning)';
      case 'INFO': return 'var(--secondary)';
      default: return 'var(--text-muted)';
    }
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem' }}>Live Log Stream</h1>
        <div className="glass" style={{ padding: '0.5rem 1rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          {logs.length} logs buffered
        </div>
      </div>

      <div className="glass" style={{ 
        height: 'calc(100vh - 10rem)', 
        overflowY: 'auto', 
        padding: '1rem',
        fontFamily: 'monospace',
        fontSize: '0.85rem',
        background: 'rgba(15, 23, 42, 0.5)'
      }}>
        {logs.length === 0 ? (
          <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Waiting for logs...
          </div>
        ) : (
          logs.map((log: LogEntry) => (
            <div key={log.id} style={{ 
              display: 'flex', 
              gap: '1rem', 
              padding: '0.25rem 0',
              borderBottom: '1px solid rgba(255,255,255,0.03)'
            }}>
              <span style={{ color: 'var(--text-muted)', minWidth: '150px' }}>
                {format(new Date(log.timestamp), 'HH:mm:ss.SSS')}
              </span>
              <span style={{ 
                color: getLevelColor(log.log_level), 
                fontWeight: 'bold',
                minWidth: '70px'
              }}>
                {log.log_level}
              </span>
              <span style={{ color: 'var(--secondary)', minWidth: '100px' }}>
                [{log.service_id.slice(0, 8)}]
              </span>
              <span style={{ color: 'var(--text-main)' }}>{log.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
