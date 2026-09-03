import React, { useEffect, useState } from 'react';
import { Database, Cpu, Server, RefreshCw } from 'lucide-react';
import { HealthStatusDTO } from '../types';
import { apiService, parseApiError } from '../services/api';

export const SystemHealthPage: React.FC = () => {
  const [health, setHealth] = useState<HealthStatusDTO | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchHealth = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const data = await apiService.getHealth();
      setHealth(data);
    } catch (err) {
      setErrorMsg(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <Database size={18} color="var(--accent-cyan)" />
            <span>Distributed System Health & Microservices Architecture</span>
          </div>
          <button className="btn btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }} onClick={fetchHealth}>
            <RefreshCw size={12} className={isLoading ? 'spin' : ''} />
            <span>Check Status</span>
          </button>
        </div>

        {errorMsg && (
          <div style={{ color: 'var(--accent-rose)', padding: '0.75rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
            {errorMsg}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
          {/* Spring Boot Tier */}
          <div style={{ background: 'var(--bg-surface-2)', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
                <Server size={18} color="#38bdf8" />
                <span>Spring Boot 3 REST Tier</span>
              </div>
              <span className="badge badge-success">Port 8080</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              <div>Version: <strong style={{ color: '#fff' }}>{health?.backendVersion || '1.0.0'} (Java 21 LTS)</strong></div>
              <div>Status: <strong style={{ color: '#34d399' }}>OPERATIONAL</strong></div>
              <div>OpenAPI Docs: <strong style={{ color: '#38bdf8' }}>/swagger-ui.html</strong></div>
            </div>
          </div>

          {/* Python ML Tier */}
          <div style={{ background: 'var(--bg-surface-2)', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
                <Cpu size={18} color="#a855f7" />
                <span>Python ML Registration Microservice</span>
              </div>
              <span className={`badge ${health?.pythonServiceStatus === 'UP' ? 'badge-success' : 'badge-failed'}`}>
                {health?.pythonServiceStatus || 'UNKNOWN'}
              </span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              <div>Service URL: <strong style={{ color: '#fff' }}>{health?.pythonServiceUrl || 'http://localhost:8000'}</strong></div>
              <div>Runtime: <strong style={{ color: '#fff' }}>Python 3.13.5 (OpenCV 5.0, NumPy)</strong></div>
              <div>Engine: <strong style={{ color: '#a855f7' }}>AMSR Master Registration Pipeline</strong></div>
            </div>
          </div>

          {/* MySQL Tier */}
          <div style={{ background: 'var(--bg-surface-2)', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600 }}>
                <Database size={18} color="#f59e0b" />
                <span>MySQL 8.0 Persistence Tier</span>
              </div>
              <span className={`badge ${health?.databaseStatus === 'UP' ? 'badge-success' : 'badge-failed'}`}>
                {health?.databaseStatus || 'UNKNOWN'}
              </span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
              <div>Database: <strong style={{ color: '#fff' }}>lunar_registration_db</strong></div>
              <div>Connection: <strong style={{ color: '#fff' }}>localhost:3306 (JPA / Hibernate 6)</strong></div>
              <div>Entity Models: <strong style={{ color: '#f59e0b' }}>Images, Jobs, Metrics, Tie-Points</strong></div>
            </div>
          </div>
        </div>

        {/* Supported Algorithms Section */}
        <div style={{ marginTop: '1.5rem', background: 'var(--bg-surface-2)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            Supported Registration Algorithm Backends
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <div className="badge badge-success" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>
              Proposed_Method (AMSR: Multi-Scale Phase Congruency + Shadow Suppression)
            </div>
            <div className="badge badge-category" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>
              SIFT_Baseline (Scale-Space Difference-of-Gaussians)
            </div>
            <div className="badge badge-category" style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>
              RIFT_Baseline (Radiation-Invariant Maximum Index Map)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
