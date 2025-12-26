import { useState } from 'react';
import SparseBrain from './components/SparseBrain';
import GraphBrain from './components/GraphBrain';
import HebbianAnimator from './components/HebbianAnimator';
import PathfinderLive from './components/PathfinderLive';
import ComparisonTool from './components/ComparisonTool';
import './App.css';

function App() {
  const [activeModule, setActiveModule] = useState<'sparse' | 'graph' | 'hebbian' | 'pathfinder' | 'compare'>('sparse');

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
      </nav>

      <main className="app-main">
        {activeModule === 'sparse' && <SparseBrain />}
        {activeModule === 'graph' && <GraphBrain />}
        {activeModule === 'hebbian' && <HebbianAnimator />}
        {activeModule === 'pathfinder' && <PathfinderLive />}
        {activeModule === 'compare' && <ComparisonTool />}
      </main>

      <footer className="app-footer">
        <p>
          Built for Synaptix Frontier AI Hackathon | Track 2
        </p>
        <p className="text-muted">
          Based on <a href="https://arxiv.org/abs/2509.26507" target="_blank" rel="noopener noreferrer">
            The Dragon Hatchling
          </a> by Kosowski et al.
        </p>
      </footer>
    </div>
  );
}

export default App;
