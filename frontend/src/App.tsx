import { useState, useEffect } from 'react';
import { Layout } from './components/Layout';
import { LogsPage } from './pages/LogsPage';
import { IncidentsPage } from './pages/IncidentsPage';
import { ServicesPage } from './pages/ServicesPage';
import { useWebSocket } from './hooks/useWebSocket';
import { useStore } from './store/useStore';

function Dashboard() {
  const incidents = useStore(state => state.incidents) || [];
  const logs = useStore(state => state.logs) || [];
  const setIncidents = useStore(state => state.setIncidents);
  const [servicesCount, setServicesCount] = useState(0);
  
  const openIncidentsCount = Array.isArray(incidents) 
    ? incidents.filter(i => i.status === 'OPEN' || i.status === 'ANALYZING').length 
    : 0;

  useEffect(() => {
    fetch('/api/services')
      .then(res => res.ok ? res.json() : [])
      .then(data => setServicesCount(Array.isArray(data) ? data.length : 0))
      .catch(() => setServicesCount(0));

    fetch('/api/incidents')
      .then(res => res.ok ? res.json() : [])
      .then(data => setIncidents(Array.isArray(data) ? data : []))
      .catch(() => setIncidents([]));
  }, [setIncidents]);

  return (
    <div className="animate-fade-in">
      <h1 style={{ fontSize: '2rem', marginBottom: '2rem' }}>System Overview</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        <div className="glass" style={{ padding: '2rem' }}>
          <h3 style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>Active Services</h3>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>{servicesCount}</div>
        </div>
        <div className="glass" style={{ padding: '2rem' }}>
          <h3 style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>Open Incidents</h3>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: openIncidentsCount > 0 ? 'var(--warning)' : 'var(--text-main)' }}>
            {openIncidentsCount}
          </div>
        </div>
        <div className="glass" style={{ padding: '2rem' }}>
          <h3 style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>Log Buffer</h3>
          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--secondary)' }}>
            {logs.length}
          </div>
        </div>
      </div>
      
      <div style={{ marginTop: '2rem', padding: '2rem' }} className="glass">
        <h3>Recent Activity</h3>
        <p style={{ marginTop: '1rem', color: 'var(--text-muted)' }}>
          {openIncidentsCount > 0 
            ? `Critical: ${openIncidentsCount} active incidents require attention.` 
            : "All systems operational. No active anomalies detected."}
        </p>
      </div>
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  
  // Initialize WebSocket connection globally
  useWebSocket();

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard': return <Dashboard />;
      case 'logs': return <LogsPage />;
      case 'incidents': return <IncidentsPage />;
      case 'services': return <ServicesPage />;
      default: return <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>Page not found.</div>;
    }
  };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderContent()}
    </Layout>
  );
}

export default App;
