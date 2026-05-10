import { useEffect, useState } from 'react';
import { Service } from '../store/useStore';
import { format } from 'date-fns';
import { Server, Activity, ShieldCheck, ShieldAlert } from 'lucide-react';

export function ServicesPage() {
  const [services, setServices] = useState<Service[]>([]);

  const fetchServices = async () => {
    try {
      const res = await fetch('/api/services');
      if (!res.ok) throw new Error('API Error');
      const data = await res.json();
      setServices(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to fetch services:', err);
      setServices([]);
    }
  };

  useEffect(() => {
    fetchServices();
    const interval = setInterval(fetchServices, 10000);
    return () => clearInterval(interval);
  }, []);

  const getStatus = (lastSeenAt: string | undefined) => {
    if (!lastSeenAt) return 'offline';
    const lastSeen = new Date(lastSeenAt).getTime();
    const now = new Date().getTime();
    // 5 minutes timeout
    return (now - lastSeen) < (5 * 60 * 1000) ? 'online' : 'offline';
  };

  return (
    <div className="animate-fade-in">
      <h1 style={{ fontSize: '2rem', marginBottom: '2rem' }}>Registered Services</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem' }}>
        {services.map((service) => {
          const status = getStatus(service.last_seen_at);
          return (
            <div key={service.id} className="glass" style={{ padding: '1.5rem', display: 'flex', gap: '1rem' }}>
              <div style={{ 
                padding: '1rem', 
                borderRadius: '12px', 
                background: 'rgba(255,255,255,0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Server size={24} color="var(--primary)" />
              </div>

              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <h3 style={{ fontSize: '1.1rem', marginBottom: '0.25rem' }}>{service.name}</h3>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.4rem', 
                    fontSize: '0.75rem',
                    fontWeight: 'bold',
                    textTransform: 'uppercase',
                    color: status === 'online' ? 'var(--success)' : 'var(--error)'
                  }}>
                    <Activity size={12} />
                    {status}
                  </div>
                </div>
                
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                  ID: {service.id.slice(0, 8)} • Env: {service.environment}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {status === 'online' ? <ShieldCheck size={14} color="var(--success)" /> : <ShieldAlert size={14} color="var(--error)" />}
                  Last seen: {service.last_seen_at ? format(new Date(service.last_seen_at), 'HH:mm:ss') : 'Never'}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
