import React from 'react';
import { BenchmarkExplorer } from '../components/experiments/BenchmarkExplorer';

export const BenchmarksPage: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <BenchmarkExplorer />
    </div>
  );
};
