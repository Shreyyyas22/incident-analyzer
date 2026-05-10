import React from 'react';
import { LayoutDashboard, Terminal, AlertCircle, Server, Activity } from 'lucide-react';
import { useStore } from '../store/useStore';

interface LayoutProps {
  children: React.ReactNode;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export function Layout({ children, activeTab, setActiveTab }: LayoutProps) {
  const isWsConnected = useStore(state => state.isWsConnected);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'logs', label: 'Live Logs', icon: Terminal },
    { id: 'incidents', label: 'Incidents', icon: AlertCircle },
    { id: 'services', label: 'Services', icon: Server },
  ];

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <aside className="glass" style={{
        width: '260px',
        margin: '1rem',
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '2rem',
        position: 'sticky',
        top: '1rem',
        height: 'calc(100vh - 2rem)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '0.5rem' }}>
          <Activity size={32} color="var(--primary)" />
          <h2 style={{ fontSize: '1.25rem', letterSpacing: '-0.02em' }}>Sentinel AI</h2>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '0.75rem 1rem',
                border: 'none',
                background: activeTab === item.id ? 'var(--primary)' : 'transparent',
                color: activeTab === item.id ? 'white' : 'var(--text-muted)',
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                width: '100%',
                textAlign: 'left',
              }}
            >
              <item.icon size={20} />
              <span style={{ fontWeight: 500 }}>{item.label}</span>
            </button>
          ))}
        </nav>

        <div style={{ marginTop: 'auto', padding: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem' }}>
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: isWsConnected ? 'var(--success)' : 'var(--error)',
              boxShadow: isWsConnected ? '0 0 8px var(--success)' : 'none'
            }} />
            <span style={{ color: 'var(--text-muted)' }}>
              {isWsConnected ? 'Stream Connected' : 'Stream Disconnected'}
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, padding: '1rem 2rem 1rem 1rem', overflowY: 'auto' }}>
        {children}
      </main>
    </div>
  );
}
