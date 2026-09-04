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
          padding: '1rem 1.5rem',
          textAlign: 'center',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          background: 'var(--bg-surface-1)',
        }}
      >
        LUNARIS-X (SIH26166) — ISRO Chandrayaan-2 Multi-Modal Sub-Pixel Image Registration Engine.
      </footer>
    </div>
  );
};

export default App;
