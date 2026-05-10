import { create } from 'zustand'

export type LogLevel = 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';

export interface LogEntry {
  id: string;
  service_id: string;
  log_level: LogLevel;
  message: string;
  timestamp: string;
  metadata?: Record<string, any>;
  trace_id?: string;
}

export interface Incident {
  id: string;
  service_id: string;
  status: 'OPEN' | 'ANALYZING' | 'ANALYZED' | 'RESOLVED' | 'IGNORED';
  summary?: string;
  severity?: string;
  analysis?: any;
  created_at: string;
}

export interface Service {
  id: string;
  name: string;
  environment: string;
  status: 'online' | 'offline' | 'error';
  last_seen_at?: string;
}

interface AppState {
  logs: LogEntry[];
  incidents: Incident[];
  services: Service[];
  isWsConnected: boolean;
  
  // Actions
  addLog: (log: LogEntry) => void;
  setIncidents: (incidents: Incident[]) => void;
  setServices: (services: Service[]) => void;
  setWsConnected: (status: boolean) => void;
  addIncident: (incident: Incident) => void;
  updateIncident: (incident: Incident) => void;
}

export const useStore = create<AppState>((set) => ({
  logs: [],
  incidents: [],
  services: [],
  isWsConnected: false,

  addLog: (log) => set((state) => ({
    logs: [log, ...state.logs].slice(0, 500) // Buffer last 500
  })),

  setIncidents: (incidents) => set({ incidents }),
  setServices: (services) => set({ services }),
  setWsConnected: (status) => set({ isWsConnected: status }),
  
  addIncident: (incident) => set((state) => ({
    incidents: [incident, ...state.incidents]
  })),

  updateIncident: (updatedIncident) => set((state) => ({
    incidents: state.incidents.map(inc => 
      inc.id === updatedIncident.id ? updatedIncident : inc
    )
  })),
}))
