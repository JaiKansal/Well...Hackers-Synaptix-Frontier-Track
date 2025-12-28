import { useState } from 'react';
import SparseBrain from './components/SparseBrain';
import GraphBrain from './components/GraphBrain';
import HebbianAnimator from './components/HebbianAnimator';
import PathfinderLive from './components/PathfinderLive';
import ComparisonTool from './components/ComparisonTool';
import Resources from './components/Resources';
import ModelStatus from './components/ModelStatus';
import './App.css';

function App() {
  const [activeModule, setActiveModule] = useState<'sparse' | 'graph' | 'hebbian' | 'pathfinder' | 'compare' | 'resources'>('sparse');

  return (
    <div className="app">
      <header className="app-header glass-card">
        <div className="header-content">
          <h1 className="app-title">🧠 BDH Brain Explorer</h1>
          <p className="app-subtitle">
            Interactive Visualization of the Baby Dragon Hatchling Architecture
          </p>
        </div>
      </header>

      <nav className="app-nav glass-card">
        <button
          className={`nav-btn ${activeModule === 'sparse' ? 'active' : ''}`}
          onClick={() => setActiveModule('sparse')}
        >
          Sparse Brain
        </button>
        <button
          className={`nav-btn ${activeModule === 'graph' ? 'active' : ''}`}
          onClick={() => setActiveModule('graph')}
        >
          Graph Brain
        </button>
        <button
          className={`nav-btn ${activeModule === 'hebbian' ? 'active' : ''}`}
          onClick={() => setActiveModule('hebbian')}
        >
          Hebbian Animator
        </button>
        <button
          className={`nav-btn ${activeModule === 'pathfinder' ? 'active' : ''}`}
          onClick={() => setActiveModule('pathfinder')}
        >
          Pathfinder Live
        </button>
        <button
          className={`nav-btn ${activeModule === 'compare' ? 'active' : ''}`}
          onClick={() => setActiveModule('compare')}
        >
          Comparison Tool
        </button>
        <button
          className={`nav-btn ${activeModule === 'resources' ? 'active' : ''}`}
          onClick={() => setActiveModule('resources')}
        >
          📚 Resources
        </button>
      </nav>

      <div className="container" style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 2rem' }}>
        <ModelStatus />
      </div>

      <main className="app-main">
        {activeModule === 'sparse' && <SparseBrain />}
        {activeModule === 'graph' && <GraphBrain />}
        {activeModule === 'hebbian' && <HebbianAnimator />}
        {activeModule === 'pathfinder' && <PathfinderLive />}
        {activeModule === 'compare' && <ComparisonTool />}
        {activeModule === 'resources' && <Resources />}
      </main>

      <footer className="app-footer">
        <p>
          Built for <strong>Synaptix Frontier AI Hackathon</strong> | Track 2: Visualization & Education
        </p>
        <p className="text-muted">
          Based on{' '}
          <a href="https://arxiv.org/abs/2509.26507" target="_blank" rel="noopener noreferrer">
            The Dragon Hatchling
          </a>{' '}
          by Kosowski et al. | Built on{' '}
          <a href="https://github.com/krychu/bdh" target="_blank" rel="noopener noreferrer">
            krychu/bdh
          </a>{' '}
          educational fork
        </p>
        <p className="text-muted" style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>
          Open Source | MIT License | See{' '}
          <span
            onClick={() => setActiveModule('resources')}
            style={{ color: '#818cf8', cursor: 'pointer', textDecoration: 'underline' }}
          >
            Resources
          </span>{' '}
          for full citations
        </p>
      </footer>
    </div>
  );
}

export default App;
