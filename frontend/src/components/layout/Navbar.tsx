import React from 'react';
import { Layers, Activity, Database, Compass, ShieldCheck } from 'lucide-react';
import { HealthStatusDTO } from '../../types';

interface NavbarProps {
  activeTab: 'workspace' | 'benchmarks' | 'system';
  setActiveTab: (tab: 'workspace' | 'benchmarks' | 'system') => void;
  health: HealthStatusDTO | null;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, health }) => {
  const isAllHealthy = health?.status === 'UP';

  return (
    <header className="app-header">
      <div className="brand-container">
        <div className="brand-logo">
          <Compass size={20} />
        </div>
        <div>
          <div className="brand-title">LUNARIS-X — Lunar Image Registration Engine</div>
          <div className="brand-subtitle">Chandrayaan-2 Multi-Modal Alignment Platform (SIH26166)</div>
        </div>
      </div>

      <nav className="nav-tabs">
        <button
          className={`nav-tab-btn ${activeTab === 'workspace' ? 'active' : ''}`}
          onClick={() => setActiveTab('workspace')}
        >
          <Layers size={16} />
          <span>Registration Workspace</span>
        </button>

        <button
          className={`nav-tab-btn ${activeTab === 'benchmarks' ? 'active' : ''}`}
          onClick={() => setActiveTab('benchmarks')}
        >
          <Activity size={16} />
          <span>Benchmark Registry</span>
        </button>

        <button
          className={`nav-tab-btn ${activeTab === 'system' ? 'active' : ''}`}
          onClick={() => setActiveTab('system')}
        >
          <Database size={16} />
          <span>System Health</span>
        </button>
      </nav>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div
          className={`badge ${isAllHealthy ? 'badge-success' : 'badge-degraded'}`}
          title={`Backend: ${health?.status || 'UNKNOWN'} | Python ML: ${health?.pythonServiceStatus || 'DOWN'} | DB: ${health?.databaseStatus || 'DOWN'}`}
        >
          <ShieldCheck size={12} />
          <span>{isAllHealthy ? 'Engine Online' : 'Services Degraded'}</span>
        </div>
      </div>
    </header>
  );
};
