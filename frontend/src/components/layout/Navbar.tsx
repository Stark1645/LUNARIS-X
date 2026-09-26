import React from 'react';
import { Layers, Activity, Database, Compass, ExternalLink } from 'lucide-react';
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
      {/* Brand */}
      <div className="brand-container">
        <div className="brand-logo">
          <Compass size={18} />
        </div>
        <div>
          <div className="brand-title">
            <span>LUNARIS-X</span>
            <span className="brand-tag">CH-2 ENGINE</span>
          </div>
        </div>
      </div>

      {/* Segmented Pill Navigation */}
      <nav className="nav-tabs">
        <button
          className={`nav-tab-btn ${activeTab === 'workspace' ? 'active' : ''}`}
          onClick={() => setActiveTab('workspace')}
        >
          <Layers size={14} />
          <span>Workspace</span>
        </button>

        <button
          className={`nav-tab-btn ${activeTab === 'benchmarks' ? 'active' : ''}`}
          onClick={() => setActiveTab('benchmarks')}
        >
          <Activity size={14} />
          <span>Benchmarks</span>
        </button>

        <button
          className={`nav-tab-btn ${activeTab === 'system' ? 'active' : ''}`}
          onClick={() => setActiveTab('system')}
        >
          <Database size={14} />
          <span>System Health</span>
        </button>
      </nav>

      {/* Status & Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <a
          href="https://pradan.issdc.gov.in"
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-secondary"
          style={{ padding: '0.35rem 0.75rem', fontSize: '0.76rem' }}
          title="Open Official ISRO ISSDC PRADAN Planetary Data Portal"
        >
          <span>ISRO PRADAN</span>
          <ExternalLink size={12} style={{ color: 'var(--text-muted)' }} />
        </a>

        <div
          className={`badge ${isAllHealthy ? 'badge-success' : 'badge-degraded'}`}
          title={`Backend: ${health?.status || 'UNKNOWN'} | Python ML: ${health?.pythonServiceStatus || 'DOWN'} | DB: ${health?.databaseStatus || 'DOWN'}`}
        >
          <span className={`status-dot ${isAllHealthy ? 'green' : 'amber'}`} />
          <span>{isAllHealthy ? 'Online' : 'Degraded'}</span>
        </div>
      </div>
    </header>
  );
};
