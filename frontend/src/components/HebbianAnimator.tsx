/**
 * Hebbian Animator Component
 * 
 * Visualizes Hebbian learning and synapse strengthening in BDH
 * Shows how synapses strengthen when neurons co-activate
 * "Neurons that fire together, wire together"
 */

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { useBDHInference } from '../hooks/useBDH';
import './HebbianAnimator.css';

interface HebbianAnimatorProps {
    inputTokens?: number[];
}

const HebbianAnimator: React.FC<HebbianAnimatorProps> = ({
    inputTokens = [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]
}) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const { infer, loading, error, data } = useBDHInference();
    const [currentLayer, setCurrentLayer] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [playbackSpeed, setPlaybackSpeed] = useState(500);

    // Run inference on mount
    useEffect(() => {
        infer({ input_tokens: inputTokens, track_states: true });
    }, []);

    // Auto-play animation
    useEffect(() => {
        if (!isPlaying || !data) return;

        const interval = setInterval(() => {
            setCurrentLayer(prev => {
                if (prev >= (data.states?.y_activations.length || 1) - 1) {
                    setIsPlaying(false);
                    return 0;
                }
                return prev + 1;
            });
        }, playbackSpeed);

        return () => clearInterval(interval);
    }, [isPlaying, data, playbackSpeed]);

    // Visualize synapse strengthening
    useEffect(() => {
        if (!data || !data.states || !svgRef.current) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();

        const width = 800;
        const height = 400;
        const margin = { top: 40, right: 40, bottom: 60, left: 80 };

        // Get activations for current layer
        const yActivations = data.states.y_activations[currentLayer];

        // Sample neurons for visualization (show 50 neurons)
        const maxNeurons = 50;
        const numNeurons = yActivations[0].length;
        const neuronStep = Math.ceil(numNeurons / maxNeurons);

        // Sample neurons
        const sampledIndices = Array.from(
            { length: Math.min(maxNeurons, numNeurons) },
            (_, i) => i * neuronStep
        );

        // Compute synapse strength (correlation between neurons)
        const synapseStrength: number[][] = [];
        for (let i = 0; i < sampledIndices.length; i++) {
            synapseStrength[i] = [];
            for (let j = 0; j < sampledIndices.length; j++) {
                if (i === j) {
                    synapseStrength[i][j] = 0;
                    continue;
                }

                // Compute co-activation across tokens
                let coActivation = 0;
                for (let t = 0; t < yActivations.length; t++) {
                    const act1 = yActivations[t][sampledIndices[i]];
                    const act2 = yActivations[t][sampledIndices[j]];
                    coActivation += (act1 > 0 && act2 > 0) ? act1 * act2 : 0;
                }
                synapseStrength[i][j] = coActivation;
            }
        }

        // Normalize
        const maxStrength = d3.max(synapseStrength.flat()) || 1;
        const normalizedStrength = synapseStrength.map(row =>
            row.map(val => val / maxStrength)
        );

        // Create scales
        const cellSize = Math.min(
            (width - margin.left - margin.right) / sampledIndices.length,
            (height - margin.top - margin.bottom) / sampledIndices.length
        );

        const xScale = d3.scaleBand()
            .domain(sampledIndices.map(String))
            .range([margin.left, margin.left + cellSize * sampledIndices.length])
            .padding(0.05);

        const yScale = d3.scaleBand()
            .domain(sampledIndices.map(String))
            .range([margin.top, margin.top + cellSize * sampledIndices.length])
            .padding(0.05);

        // Color scale
        const colorScale = d3.scaleSequential(d3.interpolateYlOrRd)
            .domain([0, 1]);

        // Draw heatmap
        const g = svg.append('g');

        // Title
        g.append('text')
            .attr('x', width / 2)
            .attr('y', 20)
            .attr('text-anchor', 'middle')
            .attr('class', 'heatmap-title')
            .text(`Synapse Strength Matrix - Layer ${currentLayer + 1}`);

        // Cells
        g.selectAll('rect')
            .data(normalizedStrength.flatMap((row, i) =>
                row.map((value, j) => ({ i, j, value }))
            ))
            .join('rect')
            .attr('x', d => xScale(String(sampledIndices[d.j]))!)
            .attr('y', d => yScale(String(sampledIndices[d.i]))!)
            .attr('width', xScale.bandwidth())
            .attr('height', yScale.bandwidth())
            .attr('fill', d => d.value > 0 ? colorScale(d.value) : '#1e293b')
            .attr('stroke', '#0f172a')
            .attr('stroke-width', 0.5)
            .style('opacity', 0)
            .transition()
            .duration(300)
            .style('opacity', 1)
            .on('end', function () {
                d3.select(this)
                    .on('mouseover', function (event, d: any) {
                        d3.select(this)
                            .attr('stroke', '#f59e0b')
                            .attr('stroke-width', 2);

                        // Show tooltip
                        const tooltip = d3.select('#hebbian-tooltip');
                        tooltip
                            .style('display', 'block')
                            .style('left', (event.pageX + 10) + 'px')
                            .style('top', (event.pageY - 10) + 'px')
                            .html(`
                <strong>Synapse ${sampledIndices[d.i]} → ${sampledIndices[d.j]}</strong><br/>
                Strength: ${(d.value * 100).toFixed(1)}%<br/>
                ${d.value > 0.5 ? '🔥 Strong connection' : d.value > 0.2 ? '⚡ Moderate' : '💤 Weak'}
              `);
                    })
                    .on('mouseout', function () {
                        d3.select(this)
                            .attr('stroke', '#0f172a')
                            .attr('stroke-width', 0.5);

                        d3.select('#hebbian-tooltip').style('display', 'none');
                    });
            });

        // Axes labels
        g.append('text')
            .attr('x', margin.left + (cellSize * sampledIndices.length) / 2)
            .attr('y', margin.top + cellSize * sampledIndices.length + 30)
            .attr('text-anchor', 'middle')
            .attr('class', 'axis-label')
            .text('Target Neuron');

        g.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('x', -(margin.top + (cellSize * sampledIndices.length) / 2))
            .attr('y', margin.left - 40)
            .attr('text-anchor', 'middle')
            .attr('class', 'axis-label')
            .text('Source Neuron');

        // Color legend
        const legendWidth = 200;
        const legendHeight = 20;
        const legendX = width - legendWidth - margin.right;
        const legendY = height - legendHeight - 20;

        const legendScale = d3.scaleLinear()
            .domain([0, 1])
            .range([0, legendWidth]);

        const legendAxis = d3.axisBottom(legendScale)
            .ticks(5)
            .tickFormat(d => `${(d as number * 100).toFixed(0)}%`);

        const legend = g.append('g')
            .attr('transform', `translate(${legendX},${legendY})`);

        // Gradient
        const defs = svg.append('defs');
        const gradient = defs.append('linearGradient')
            .attr('id', 'legend-gradient');

        gradient.selectAll('stop')
            .data(d3.range(0, 1.1, 0.1))
            .join('stop')
            .attr('offset', d => `${d * 100}%`)
            .attr('stop-color', d => colorScale(d));

        legend.append('rect')
            .attr('width', legendWidth)
            .attr('height', legendHeight)
            .style('fill', 'url(#legend-gradient)');

        legend.append('g')
            .attr('transform', `translate(0,${legendHeight})`)
            .call(legendAxis)
            .attr('color', '#94a3b8');

    }, [data, currentLayer]);

    const strongSynapses = data?.states ? (() => {
        const yActivations = data.states.y_activations[currentLayer];
        let count = 0;
        for (let t = 0; t < yActivations.length; t++) {
            for (let i = 0; i < Math.min(50, yActivations[t].length); i++) {
                if (yActivations[t][i] > 0.5) count++;
            }
        }
        return count;
    })() : 0;

    return (
        <div className="hebbian-animator-container glass-card">
            <div className="hebbian-header">
                <h2>Hebbian Animator: Synapse Strengthening</h2>
                <p className="text-muted">
                    "Neurons that fire together, wire together" - Watch synapses strengthen through co-activation
                </p>
            </div>

            {loading && (
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Running inference...</p>
                </div>
            )}

            {error && (
                <div className="error-container">
                    <p className="error-message">Error: {error}</p>
                </div>
            )}

            {data && data.states && (
                <>
                    <div className="playback-controls glass-card">
                        <button
                            className={`btn ${isPlaying ? 'btn-secondary' : 'btn-primary'}`}
                            onClick={() => setIsPlaying(!isPlaying)}
                        >
                            {isPlaying ? '⏸ Pause' : '▶ Play'}
                        </button>

                        <button
                            className="btn btn-secondary"
                            onClick={() => setCurrentLayer(0)}
                        >
                            ⏮ Reset
                        </button>

                        <div className="speed-control">
                            <label>Speed:</label>
                            <input
                                type="range"
                                min="100"
                                max="1000"
                                step="100"
                                value={playbackSpeed}
                                onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
                                className="slider"
                            />
                            <span>{(1000 / playbackSpeed).toFixed(1)}x</span>
                        </div>

                        <div className="layer-display">
                            Layer: <strong>{currentLayer + 1}</strong> / {data.states.y_activations.length}
                        </div>
                    </div>

                    <div className="visualization-container">
                        <svg
                            ref={svgRef}
                            width="800"
                            height="400"
                            className="hebbian-svg"
                        />
                        <div id="hebbian-tooltip" className="tooltip"></div>
                    </div>

                    <div className="metrics-grid">
                        <div className="metric-card glass-card">
                            <div className="metric-label">Current Layer</div>
                            <div className="metric-value">{currentLayer + 1}</div>
                            <div className="metric-subtitle">of {data.states.y_activations.length}</div>
                        </div>

                        <div className="metric-card glass-card">
                            <div className="metric-label">Strong Synapses</div>
                            <div className="metric-value">{strongSynapses}</div>
                            <div className="metric-subtitle">High co-activation</div>
                        </div>

                        <div className="metric-card glass-card">
                            <div className="metric-label">Learning Rule</div>
                            <div className="metric-value">Hebbian</div>
                            <div className="metric-subtitle">Δσ ∝ y·yᵀ</div>
                        </div>

                        <div className="metric-card glass-card">
                            <div className="metric-label">Memory Type</div>
                            <div className="metric-value">Dynamic</div>
                            <div className="metric-subtitle">Context-dependent</div>
                        </div>
                    </div>

                    <div className="insights glass-card">
                        <h3>Key Insights</h3>
                        <ul>
                            <li>
                                <strong>Hebbian Learning:</strong> Synapses strengthen when pre- and post-synaptic neurons
                                activate together. This is the fundamental learning rule in BDH's working memory.
                            </li>
                            <li>
                                <strong>Dynamic Memory:</strong> Unlike Transformers' static KV-cache, BDH's σ matrix
                                evolves during inference, adapting to the current context.
                            </li>
                            <li>
                                <strong>Monosemanticity:</strong> Bright cells in the heatmap represent strong synapse-concept
                                associations. Each synapse tends to encode a specific relationship.
                            </li>
                            <li>
                                <strong>Biological Plausibility:</strong> This learning mechanism mirrors how real neurons
                                in the brain form memories through synaptic plasticity.
                            </li>
                        </ul>
                    </div>
                </>
            )}
        </div>
    );
};

export default HebbianAnimator;
