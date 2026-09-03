import React, { useEffect, useState } from 'react';
import { Activity, Download, RefreshCw } from 'lucide-react';
import { ExperimentDTO } from '../../types';
import { apiService, parseApiError } from '../../services/api';

export const BenchmarkExplorer: React.FC = () => {
  const [experiments, setExperiments] = useState<ExperimentDTO[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [selectedSuite, setSelectedSuite] = useState<string>('ALL');
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const loadExperiments = async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const data = await apiService.getAllExperiments();
      setExperiments(data);
    } catch (err) {
      setErrorMsg(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadExperiments();
  }, []);

  const filteredExperiments = experiments.filter((exp) => {
    if (selectedSuite !== 'ALL' && exp.suiteName !== selectedSuite) return false;
    if (selectedAlgorithm !== 'ALL') {
      const configOrAlgo = exp.configurationName || exp.algorithm;
      if (!configOrAlgo.toLowerCase().includes(selectedAlgorithm.toLowerCase())) return false;
    }
    if (searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase();
      return exp.pairName.toLowerCase().includes(q) || exp.suiteName.toLowerCase().includes(q);
    }
    return true;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'SUCCESS':
        return <span className="badge badge-success">SUCCESS</span>;
      case 'DEGRADED':
        return <span className="badge badge-degraded">DEGRADED</span>;
      case 'FAILED':
        return <span className="badge badge-failed">FAILED</span>;
      default:
        return <span className="badge badge-category">{status}</span>;
    }
  };

  const exportCsv = () => {
    const headers = ['Suite', 'Pair', 'Algorithm', 'Category', 'Inliers', 'Ratio (%)', 'Inlier RMSE (px)', 'GT RMSE (px)', 'Gini (Gk)', 'Latency (ms)', 'Status'];
    const rows = filteredExperiments.map((e) => [
      e.suiteName,
      e.pairName,
      e.configurationName || e.algorithm,
      e.dataCategory,
      e.inlierCount,
      e.inlierRatioPercent?.toFixed(1) || 'N/A',
      e.rmseInliersPx?.toFixed(2) || 'N/A',
      e.rmseGroundTruthPx?.toFixed(2) || 'N/A',
      e.spatialGini?.toFixed(2) || 'N/A',
      e.latencyMs?.toFixed(0) || 'N/A',
      e.status,
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `lunar_benchmark_experiments_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="card">
      <div className="card-header" style={{ flexWrap: 'wrap', gap: '0.75rem' }}>
        <div className="card-title">
          <Activity size={18} color="var(--accent-cyan)" />
          <span>Scientific Benchmark & Ablation Registry (Ch-2-MatchBench)</span>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <button className="btn btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }} onClick={loadExperiments}>
            <RefreshCw size={12} className={isLoading ? 'spin' : ''} />
            <span>Refresh</span>
          </button>

          <button className="btn btn-primary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }} onClick={exportCsv}>
            <Download size={12} />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {errorMsg && (
        <div style={{ color: 'var(--accent-rose)', padding: '0.65rem 0.85rem', background: 'rgba(239, 68, 68, 0.1)', borderRadius: 'var(--radius-sm)', marginBottom: '0.75rem' }}>
          {errorMsg}
        </div>
      )}

      {/* Filter Controls */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', marginBottom: '1rem', background: 'var(--bg-surface-2)', padding: '0.75rem', borderRadius: 'var(--radius-md)' }}>
        <div>
          <label className="form-label" style={{ fontSize: '0.7rem' }}>Benchmark Suite</label>
          <select className="form-select" value={selectedSuite} onChange={(e) => setSelectedSuite(e.target.value)}>
            <option value="ALL">All Suites (A through E)</option>
            <option value="suite_a_intra_sensor">Suite A: Intra-Sensor (Same Sun)</option>
            <option value="suite_b_sun_angle">Suite B: Sun Angle Variation</option>
            <option value="suite_c_scale_disparity">Suite C: Scale Disparity (4x - 20x)</option>
            <option value="suite_d_cross_modal">Suite D: Cross-Modal (SWIR vs Pan)</option>
            <option value="suite_e_difficult_terrain">Suite E: Difficult Terrain</option>
          </select>
        </div>

        <div>
          <label className="form-label" style={{ fontSize: '0.7rem' }}>Algorithm / Configuration</label>
          <select className="form-select" value={selectedAlgorithm} onChange={(e) => setSelectedAlgorithm(e.target.value)}>
            <option value="ALL">All Algorithms</option>
            <option value="Proposed">Proposed AMSR Engine</option>
            <option value="SIFT">SIFT Baseline</option>
            <option value="RIFT">RIFT Baseline</option>
            <option value="Ablation">Ablation Studies</option>
          </select>
        </div>

        <div>
          <label className="form-label" style={{ fontSize: '0.7rem' }}>Search Pair Name</label>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. scale_4x, sun_angle..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Suite</th>
              <th>Test Pair</th>
              <th>Configuration / Algorithm</th>
              <th>Category</th>
              <th>Inliers</th>
              <th>Inlier Ratio</th>
              <th>Inlier RMSE</th>
              <th>GT RMSE</th>
              <th>Gini (G_k)</th>
              <th>Latency</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredExperiments.length === 0 ? (
              <tr>
                <td colSpan={11} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                  {isLoading ? 'Loading experiment records...' : 'No benchmark records match the selected filters.'}
                </td>
              </tr>
            ) : (
              filteredExperiments.map((exp) => (
                <tr key={exp.id || exp.experimentId}>
                  <td style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>{exp.suiteName.replace('suite_', '')}</td>
                  <td style={{ fontWeight: 500 }}>{exp.pairName}</td>
                  <td>
                    <span style={{ fontWeight: 600, color: exp.configurationName?.includes('Proposed') || exp.algorithm?.includes('Proposed') ? '#38bdf8' : 'var(--text-primary)' }}>
                      {exp.configurationName || exp.algorithm}
                    </span>
                  </td>
                  <td>
                    <span className="badge badge-category" style={{ fontSize: '0.65rem' }}>{exp.dataCategory}</span>
                  </td>
                  <td className="font-mono" style={{ color: '#34d399', fontWeight: 600 }}>{exp.inlierCount}</td>
                  <td className="font-mono">{exp.inlierRatioPercent ? `${exp.inlierRatioPercent.toFixed(1)}%` : 'N/A'}</td>
                  <td className="font-mono">{exp.rmseInliersPx !== null ? `${exp.rmseInliersPx.toFixed(2)} px` : 'N/A'}</td>
                  <td className="font-mono" style={{ color: exp.rmseGroundTruthPx !== null && exp.rmseGroundTruthPx <= 5.0 ? '#34d399' : '#fbbf24' }}>
                    {exp.rmseGroundTruthPx !== null ? `${exp.rmseGroundTruthPx.toFixed(2)} px` : 'N/A'}
                  </td>
                  <td className="font-mono">{exp.spatialGini !== null ? exp.spatialGini.toFixed(2) : 'N/A'}</td>
                  <td className="font-mono">{exp.latencyMs !== null ? `${exp.latencyMs.toFixed(0)} ms` : 'N/A'}</td>
                  <td>{getStatusBadge(exp.status)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
