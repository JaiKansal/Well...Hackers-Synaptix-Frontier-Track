/**
 * Pathfinder Live Component
 * 
 * Interactive maze builder and BDH pathfinding visualization
 * Shows attention flow, neuron firing, and real-time sparsity
 */

import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './PathfinderLive.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

type CellType = 'empty' | 'wall' | 'start' | 'end' | 'path';

interface Cell {
    row: number;
    col: number;
    type: CellType;
}

interface PathfinderResponse {
    solution: number[][];
    predictions: number[];
    states?: any;
    sparsity?: any;
}

const PathfinderLive: React.FC = () => {
    const [gridSize] = useState(10);
    const [grid, setGrid] = useState<Cell[][]>([]);
    const [startPos, setStartPos] = useState<[number, number] | null>(null);
    const [endPos, setEndPos] = useState<[number, number] | null>(null);
    const [isDrawing, setIsDrawing] = useState(false);
    const [drawMode, setDrawMode] = useState<'wall' | 'erase'>('wall');
    const [solution, setSolution] = useState<number[][] | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [sparsity, setSparsity] = useState<number>(0);
    const [activeNeurons, setActiveNeurons] = useState<number>(0);


    const canvasRef = useRef<HTMLCanvasElement>(null);

    // Initialize grid
    useEffect(() => {
        const newGrid: Cell[][] = [];
        for (let row = 0; row < gridSize; row++) {
            newGrid[row] = [];
            for (let col = 0; col < gridSize; col++) {
                newGrid[row][col] = { row, col, type: 'empty' };
            }
        }
        setGrid(newGrid);

        // Set default start and end
        setStartPos([0, 0]);
        setEndPos([gridSize - 1, gridSize - 1]);
        newGrid[0][0].type = 'start';
        newGrid[gridSize - 1][gridSize - 1].type = 'end';
    }, [gridSize]);

    // Draw grid on canvas
    useEffect(() => {
        if (!canvasRef.current || grid.length === 0) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const cellSize = canvas.width / gridSize;

        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw cells
        grid.forEach((row, rowIdx) => {
            row.forEach((cell, colIdx) => {
                const x = colIdx * cellSize;
                const y = rowIdx * cellSize;

                // Fill color based on cell type
                switch (cell.type) {
                    case 'wall':
                        ctx.fillStyle = '#334155';
                        break;
                    case 'start':
                        ctx.fillStyle = '#10b981';
                        break;
                    case 'end':
                        ctx.fillStyle = '#ef4444';
                        break;
                    case 'path':
                        ctx.fillStyle = '#6366f1';
                        break;
                    default:
                        ctx.fillStyle = '#1e293b';
                }

                ctx.fillRect(x, y, cellSize - 1, cellSize - 1);

                // Draw grid lines
                ctx.strokeStyle = '#0f172a';
                ctx.strokeRect(x, y, cellSize - 1, cellSize - 1);
            });
        });

        // Draw solution path if exists
        if (solution) {
            ctx.strokeStyle = '#8b5cf6';
            ctx.lineWidth = 3;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';

            ctx.beginPath();
            solution.forEach((pos, idx) => {
                const [row, col] = pos;
                const x = (col + 0.5) * cellSize;
                const y = (row + 0.5) * cellSize;

                if (idx === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            ctx.stroke();

            // Draw dots on path
            ctx.fillStyle = '#a78bfa';
            solution.forEach(pos => {
                const [row, col] = pos;
                const x = (col + 0.5) * cellSize;
                const y = (row + 0.5) * cellSize;
                ctx.beginPath();
                ctx.arc(x, y, 4, 0, 2 * Math.PI);
                ctx.fill();
            });
        }
    }, [grid, solution, gridSize]);

    // Handle mouse events
    const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
        setIsDrawing(true);
        handleMouseMove(e);
    };

    const handleMouseUp = () => {
        setIsDrawing(false);
    };

    const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
        if (!isDrawing && e.type !== 'mousedown') return;
        if (!canvasRef.current) return;

        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const cellSize = canvas.width / gridSize;
        const col = Math.floor(x / cellSize);
        const row = Math.floor(y / cellSize);

        if (row < 0 || row >= gridSize || col < 0 || col >= gridSize) return;

        const newGrid = [...grid];
        const cell = newGrid[row][col];

        // Don't modify start/end cells
        if (cell.type === 'start' || cell.type === 'end') return;

        // Toggle wall/empty
        if (drawMode === 'wall') {
            cell.type = 'wall';
        } else {
            cell.type = 'empty';
        }

        setGrid(newGrid);
    };

    // Clear grid
    const handleClear = () => {
        const newGrid = grid.map(row =>
            row.map(cell => ({
                ...cell,
                type: (cell.type === 'start' || cell.type === 'end' ? cell.type : 'empty') as CellType
            }))
        );
        setGrid(newGrid);
        setSolution(null);
    };

    // Generate random maze
    const handleRandomMaze = () => {
        const newGrid = [...grid];
        newGrid.forEach(row => {
            row.forEach(cell => {
                if (cell.type !== 'start' && cell.type !== 'end') {
                    cell.type = Math.random() > 0.7 ? 'wall' : 'empty';
                }
            });
        });
        setGrid(newGrid);
        setSolution(null);
    };

    // Solve maze with BDH
    const handleSolve = async () => {
        if (!startPos || !endPos) {
            setError('Please set start and end positions');
            return;
        }

        setLoading(true);
        setError(null);

        try {
            // Convert grid to board format
            const board = grid.map(row =>
                row.map(cell => {
                    if (cell.type === 'wall') return 1;
                    if (cell.type === 'start') return 2;
                    if (cell.type === 'end') return 3;
                    return 0;
                })
            );

            const response = await axios.post<PathfinderResponse>(
                `${API_URL}/api/pathfind`,
                { board }
            );

            setSolution(response.data.solution);

            if (response.data.sparsity) {
                setSparsity(response.data.sparsity.y_sparsity_mean * 100);
            }

            if (response.data.states) {
                // Count active neurons
                const yActivations = response.data.states.y_activations;
                if (yActivations && yActivations.length > 0) {
                    const lastLayer = yActivations[yActivations.length - 1];
                    const active = lastLayer.flat().filter((v: number) => v > 0).length;
                    setActiveNeurons(active);
                }
            }

            // Update grid with solution path
            const newGrid = [...grid];
            response.data.solution.forEach(([row, col]) => {
                if (newGrid[row][col].type === 'empty') {
                    newGrid[row][col].type = 'path';
                }
            });
            setGrid(newGrid);

        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Failed to solve maze');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="pathfinder-container glass-card">
            <div className="pathfinder-header">
                <h2>Pathfinder Live: BDH Maze Solving</h2>
                <p className="text-muted">
                    Draw a maze and watch BDH find the optimal path with sparse activations
                </p>
            </div>

            <div className="pathfinder-content">
                <div className="maze-section">
                    <div className="maze-controls">
                        <div className="control-group">
                            <button
                                className={`btn ${drawMode === 'wall' ? 'btn-primary' : 'btn-secondary'}`}
                                onClick={() => setDrawMode('wall')}
                            >
                                🧱 Draw Walls
                            </button>
                            <button
                                className={`btn ${drawMode === 'erase' ? 'btn-primary' : 'btn-secondary'}`}
                                onClick={() => setDrawMode('erase')}
                            >
                                ✏️ Erase
                            </button>
                        </div>

                        <div className="control-group">
                            <button className="btn btn-secondary" onClick={handleClear}>
                                🗑️ Clear
                            </button>
                            <button className="btn btn-secondary" onClick={handleRandomMaze}>
                                🎲 Random Maze
                            </button>
                            <button
                                className="btn btn-primary"
                                onClick={handleSolve}
                                disabled={loading}
                            >
                                {loading ? '⏳ Solving...' : '🚀 Solve!'}
                            </button>
                        </div>
                    </div>

                    <div className="maze-canvas-container">
                        <canvas
                            ref={canvasRef}
                            width={500}
                            height={500}
                            className="maze-canvas"
                            onMouseDown={handleMouseDown}
                            onMouseUp={handleMouseUp}
                            onMouseMove={handleMouseMove}
                            onMouseLeave={handleMouseUp}
                        />

                        <div className="maze-legend">
                            <div className="legend-item">
                                <div className="legend-color" style={{ background: '#10b981' }}></div>
                                <span>Start</span>
                            </div>
                            <div className="legend-item">
                                <div className="legend-color" style={{ background: '#ef4444' }}></div>
                                <span>End</span>
                            </div>
                            <div className="legend-item">
                                <div className="legend-color" style={{ background: '#334155' }}></div>
                                <span>Wall</span>
                            </div>
                            <div className="legend-item">
                                <div className="legend-color" style={{ background: '#8b5cf6' }}></div>
                                <span>Solution Path</span>
                            </div>
                        </div>
                    </div>

                    {error && (
                        <div className="error-message">
                            ⚠️ {error}
                        </div>
                    )}
                </div>

                <div className="metrics-section">
                    <div className="metric-card glass-card">
                        <div className="metric-label">Path Length</div>
                        <div className="metric-value">{solution ? solution.length : '-'}</div>
                        <div className="metric-subtitle">Steps to goal</div>
                    </div>

                    <div className="metric-card glass-card">
                        <div className="metric-label">Sparsity</div>
                        <div className="metric-value">{sparsity.toFixed(1)}%</div>
                        <div className="metric-subtitle">Active neurons</div>
                    </div>

                    <div className="metric-card glass-card">
                        <div className="metric-label">Active Neurons</div>
                        <div className="metric-value">{activeNeurons}</div>
                        <div className="metric-subtitle">Last layer</div>
                    </div>

                    <div className="metric-card glass-card">
                        <div className="metric-label">Status</div>
                        <div className="metric-value">
                            {solution ? '✅' : loading ? '⏳' : '⏸️'}
                        </div>
                        <div className="metric-subtitle">
                            {solution ? 'Solved' : loading ? 'Solving' : 'Ready'}
                        </div>
                    </div>
                </div>
            </div>

            <div className="insights glass-card">
                <h3>How BDH Solves Mazes</h3>
                <ul>
                    <li>
                        <strong>Sparse Activation:</strong> BDH activates only ~{sparsity.toFixed(1)}% of neurons,
                        making pathfinding extremely efficient compared to dense Transformer attention.
                    </li>
                    <li>
                        <strong>Linear Attention:</strong> Unlike Transformers' O(n²) attention, BDH uses linear
                        attention, scaling efficiently with maze size.
                    </li>
                    <li>
                        <strong>Working Memory:</strong> The dynamic σ matrix stores the maze structure and
                        updates as BDH explores, similar to how humans remember paths.
                    </li>
                    <li>
                        <strong>Biological Plausibility:</strong> BDH's pathfinding mirrors how animals navigate
                        using place cells and grid cells in the hippocampus.
                    </li>
                </ul>
            </div>
        </div>
    );
};

export default PathfinderLive;
