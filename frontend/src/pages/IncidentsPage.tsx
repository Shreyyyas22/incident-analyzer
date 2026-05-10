import { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { format } from 'date-fns';
import { ChevronDown, ChevronUp, BrainCircuit, AlertTriangle, CheckCircle } from 'lucide-react';

export function IncidentsPage() {
  const incidents = useStore(state => state.incidents);
  const setIncidents = useStore(state => state.setIncidents);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const fetchIncidents = async () => {
    try {
      const res = await fetch('/api/incidents');
      if (!res.ok) throw new Error('API Error');
      const data = await res.json();
      setIncidents(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to fetch incidents:', err);
      setIncidents([]);
    }
  };

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ANALYZED': return <CheckCircle size={18} color="var(--success)" />;
      case 'ANALYZING': return <BrainCircuit size={18} color="var(--primary)" className="animate-pulse" />;
      default: return <AlertTriangle size={18} color="var(--warning)" />;
    }
  };

  return (
    <div className="animate-fade-in">
      <h1 style={{ fontSize: '2rem', marginBottom: '2rem' }}>Incidents & AI Analysis</h1>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {incidents.length === 0 ? (
          <div className="glass" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            No incidents detected. System is healthy.
          </div>
        ) : (
          incidents.map((incident) => (
            <div key={incident.id} className="glass" style={{ overflow: 'hidden' }}>
              <div
                onClick={() => setExpandedId(expandedId === incident.id ? null : incident.id)}
                style={{
                  padding: '1.25rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1.5rem',
                  cursor: 'pointer',
                  transition: 'background 0.2s'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', minWidth: '120px' }}>
                  {getStatusIcon(incident.status)}
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                    {incident.status}
                  </span>
                </div>

                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: '1.1rem', marginBottom: '0.25rem' }}>
                    {incident.summary || 'Incident detected'}
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    Service: {incident.service_id.slice(0, 8)} • {format(new Date(incident.created_at), 'MMM d, HH:mm:ss')}
                  </div>
                </div>

                {incident.severity && (
                  <div style={{
                    padding: '0.25rem 0.75rem',
                    borderRadius: '20px',
                    background: incident.severity === 'P1' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                    color: incident.severity === 'P1' ? 'var(--error)' : 'var(--warning)',
                    fontSize: '0.8rem',
                    fontWeight: 'bold',
                    border: '1px solid currentColor'
                  }}>
                    {incident.severity}
                  </div>
                )}

                {expandedId === incident.id ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
              </div>

              {expandedId === incident.id && incident.analysis && (
                <div style={{
                  padding: '1.5rem',
                  background: 'rgba(0,0,0,0.2)',
                  borderTop: '1px solid var(--border)',
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: '2rem'
                }}>
                  <div>
                    <h4 style={{ color: 'var(--primary)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <BrainCircuit size={18} /> Root Cause Analysis
                    </h4>
                    <p style={{ fontSize: '0.95rem', lineHeight: 1.6, color: 'var(--text-main)' }}>
                      {incident.analysis.root_cause}
                    </p>

                    <h4 style={{ color: 'var(--success)', marginTop: '1.5rem', marginBottom: '0.75rem' }}>Suggested Fixes</h4>
                    <ul style={{ paddingLeft: '1.25rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                      {incident.analysis.suggested_fixes?.map((fix: string, idx: number) => (
                        <li key={idx} style={{ marginBottom: '0.4rem' }}>{fix}</li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 style={{ color: 'var(--secondary)', marginBottom: '0.75rem' }}>Contributing Factors</h4>
                    <ul style={{ paddingLeft: '1.25rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                      {incident.analysis.contributing_factors?.map((factor: string, idx: number) => (
                        <li key={idx} style={{ marginBottom: '0.4rem' }}>{factor}</li>
                      ))}
                    </ul>

                    <div style={{ marginTop: '2rem', padding: '1rem', borderRadius: '8px', background: 'rgba(139, 92, 246, 0.1)', border: '1px solid var(--primary-glow)' }}>
                      <div style={{ fontSize: '0.8rem', color: 'var(--primary)', marginBottom: '0.25rem' }}>AI Confidence Score</div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{Math.round(incident.analysis.confidence_score * 100)}%</div>
                    </div>
                  </div>
                </div>
              )}

              {expandedId === incident.id && !incident.analysis && (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', borderTop: '1px solid var(--border)' }}>
                  {incident.status === 'ANALYZING' ? 'AI is performing deep analysis...' : 'No analysis available yet.'}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
