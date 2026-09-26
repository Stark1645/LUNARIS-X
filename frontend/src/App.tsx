import React, { useEffect, useState } from 'react';
import { Navbar } from './components/layout/Navbar';
import { WorkspacePage } from './pages/WorkspacePage';
import { BenchmarksPage } from './pages/BenchmarksPage';
import { SystemHealthPage } from './pages/SystemHealthPage';
import { HealthStatusDTO } from './types';
import { apiService } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'workspace' | 'benchmarks' | 'system'>('workspace');
  const [health, setHealth] = useState<HealthStatusDTO | null>(null);

  useEffect(() => {
    const fetchHealth = () => {
      apiService.getHealth()
        .then(setHealth)
        .catch(() => {
          setHealth({
            status: 'CONNECTING',
            backendVersion: '1.0.0',
            pythonServiceStatus: 'CONNECTING',
            pythonServiceUrl: 'http://localhost:8000',
            databaseStatus: 'CONNECTING',
            supportedAlgorithms: ['Proposed_Method', 'SIFT_Baseline', 'RIFT_Baseline'],
          });
        });
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} health={health} />

      <main className="main-container" style={{ flex: 1 }}>
        {activeTab === 'workspace' && <WorkspacePage />}
        {activeTab === 'benchmarks' && <BenchmarksPage />}
        {activeTab === 'system' && <SystemHealthPage />}
      </main>

      <footer
        style={{
          borderTop: '1px solid var(--border-subtle)',
          padding: '1.25rem 1.75rem',
          textAlign: 'center',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          background: 'rgba(7, 12, 22, 0.95)',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '0.4rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap', justifyContent: 'center' }}>
          <span style={{ color: 'var(--accent-isro-saffron)', fontWeight: 700, fontFamily: 'var(--font-display)' }}>
            ISRO // ISSDC CH-2 MISSION CONTROL
          </span>
          <span>•</span>
          <span style={{ color: 'var(--text-secondary)' }}>
            LUNARIS-X (SIH26166) Sub-Pixel Multi-Modal Lunar Image Registration Engine
          </span>
          <span>•</span>
          <span style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
            NASA/ISRO PDS4 COMPLIANT
          </span>
        </div>
        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          Indian Space Research Organisation (ISRO) • Department of Space, Government of India • Developed for Smart India Hackathon
        </div>
      </footer>
    </div>
  );
};

export default App;
