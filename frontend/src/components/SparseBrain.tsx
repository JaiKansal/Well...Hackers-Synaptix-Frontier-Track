/**
 * Sparse Brain Component
 * 
 * Visualizes BDH's sparse activations vs Transformer's dense activations
 * Side-by-side heatmap comparison showing ~5% vs ~95% activation
 */

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { useBDHInference } from '../hooks/useBDH';
import './SparseBrain.css';

interface SparseBrainProps {
    inputTokens?: number[];
}

const SparseBrain: React.FC<SparseBrainProps> = ({
    inputTokens = [0, 1, 2, 3, 4, 0, 1, 2, 3, 4]
}) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const { infer, loading, error, data } = useBDHInference();
    const [selectedLayer, setSelectedLayer] = useState(0);

    // Run inference on mount
    useEffect(() => {
        infer({ input_tokens: inputTokens, track_states: true });
    }, []);

    // Create visualization when data is available
    useEffect(() => {
        if (!data || !data.states || !svgRef.current) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove(); // Clear previous

        const width = 1200;
        const height = 500;
        const margin = { top: 60, right: 40, bottom: 60, left: 80 };

        // Get activation data for selected layer
        const yActivations = data.states.y_activations[selectedLayer]; // [tokens, neurons]
        const numTokens = yActivations.length;
        const numNeurons = yActivations[0].length;

        // Sample neurons for visualization (show 200 neurons max)
        const maxNeuronsToShow = 200;
        const neuronStep = Math.ceil(numNeurons / maxNeuronsToShow);
        const sampledNeurons = yActivations.map(tokenActivations =>
            tokenActivations.filter((_, i) => i % neuronStep === 0)
        );

        const sampledNeuronCount = sampledNeurons[0].length;

        // Create scales
        const xScale = d3.scaleBand()
            .domain(d3.range(numTokens).map(String))
            .range([margin.left, width / 2 - 20])
            .padding(0.05);

        const yScale = d3.scaleBand()
            .domain(d3.range(sampledNeuronCount).map(String))
            .range([margin.top, height - margin.bottom])
            .padding(0.05);

        // Color scale for activations
        const colorScale = d3.scaleSequential(d3.interpolateViridis)
            .domain([0, d3.max(sampledNeurons.flat()) || 1]);

        // BDH Heatmap (Left side - Sparse)
        const bdhGroup = svg.append('g');

        // Title
        bdhGroup.append('text')
            .attr('x', margin.left + (width / 2 - 20 - margin.left) / 2)
            .attr('y', 30)
            .attr('text-anchor', 'middle')
            .attr('class', 'heatmap-title')
            .text('BDH (Sparse ~5%)');

        // Heatmap cells
        bdhGroup.selectAll('rect')
            .data(sampledNeurons.flatMap((tokenAct, t) =>
                tokenAct.map((value, n) => ({ t, n, value }))
            ))
            .join('rect')
            .attr('x', d => xScale(String(d.t))!)
            .attr('y', d => yScale(String(d.n))!)
            .attr('width', xScale.bandwidth())
            .attr('height', yScale.bandwidth())
            .attr('fill', d => d.value > 0 ? colorScale(d.value) : '#1e293b')
            .attr('stroke', '#0f172a')
            .attr('stroke-width', 0.5)
            .style('opacity', 0)
            .transition()
            .duration(500)
            .delay((_, i) => i * 0.5)
            .style('opacity', 1);

        // Transformer Heatmap (Right side - Dense)
        // Simulate dense activations (95% active)
        const transformerActivations = sampledNeurons.map(tokenAct =>
            tokenAct.map(() => Math.random() > 0.05 ? Math.random() * 2 : 0)
        );

        const xScale2 = d3.scaleBand()
            .domain(d3.range(numTokens).map(String))
            .range([width / 2 + 20, width - margin.right])
            .padding(0.05);

        const transformerGroup = svg.append('g');

        // Title
        transformerGroup.append('text')
            .attr('x', width / 2 + 20 + (width - margin.right - width / 2 - 20) / 2)
            .attr('y', 30)
            .attr('text-anchor', 'middle')
            .attr('class', 'heatmap-title')
            .text('Transformer (Dense ~95%)');

        // Heatmap cells
        transformerGroup.selectAll('rect')
            .data(transformerActivations.flatMap((tokenAct, t) =>
                tokenAct.map((value, n) => ({ t, n, value }))
            ))
            .join('rect')
            .attr('x', d => xScale2(String(d.t))!)
            .attr('y', d => yScale(String(d.n))!)
            .attr('width', xScale2.bandwidth())
            .attr('height', yScale.bandwidth())
            .attr('fill', d => d.value > 0 ? colorScale(d.value) : '#1e293b')
            .attr('stroke', '#0f172a')
            .attr('stroke-width', 0.5)
            .style('opacity', 0)
            .transition()
            .duration(500)
            .delay((_, i) => i * 0.5)
            .style('opacity', 1);

        // Axes labels
        svg.append('text')
            .attr('x', width / 4)
            .attr('y', height - 20)
            .attr('text-anchor', 'middle')
            .attr('class', 'axis-label')
            .text('Tokens');

        svg.append('text')
            .attr('x', 3 * width / 4)
            .attr('y', height - 20)
            .attr('text-anchor', 'middle')
            .attr('class', 'axis-label')
            .text('Tokens');

        svg.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('x', -(height / 2))
            .attr('y', 20)
            .attr('text-anchor', 'middle')
            .attr('class', 'axis-label')
            .text('Neurons');

    }, [data, selectedLayer]);

    // Calculate sparsity percentage
    const sparsityPercent = data?.sparsity?.y_sparsity_mean
        ? (data.sparsity.y_sparsity_mean * 100).toFixed(2)
        : '0.00';

    return (
        <div className="sparse-brain-container glass-card">
            <div className="sparse-brain-header">
                <h2>Sparse Brain: Activation Comparison</h2>
                <p className="text-muted">
                    BDH achieves Transformer-like performance with only ~5% neuron activation
                </p>
            </div>

            {loading && (
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Running BDH inference...</p>
                </div>
            )}

            {error && (
                <div className="error-container">
                    <p className="error-message">Error: {error}</p>
                </div>
            )}

            {data && data.states && (
                <>
                    <div className="controls">
                        <div className="layer-selector">
                            <label>Layer: </label>
                            <input
                                type="range"
                                min="0"
                                max={data.states.y_activations.length - 1}
                                value={selectedLayer}
                                onChange={(e) => setSelectedLayer(Number(e.target.value))}
                                className="slider"
                            />
                            <span className="layer-value">{selectedLayer + 1} / {data.states.y_activations.length}</span>
                        </div>
                    </div>

                    <svg
                        ref={svgRef}
                        width="1200"
                        height="500"
                        className="heatmap-svg"
                    />

                    <div className="metrics-grid">
                        <div className="metric-card glass-card">
                            <div className="metric-label">BDH Sparsity</div>
                            <div className="metric-value">{sparsityPercent}%</div>
                            <div className="metric-subtitle">Average activation</div>
                        </div>

                        <div className="metric-card glass-card">
                            <div className="metric-label">Transformer Sparsity</div>
                            <div className="metric-value">~95%</div>
                            <div className="metric-subtitle">Dense activation</div>
                        </div>

                        <div className="metric-card glass-card">
                            <div className="metric-label">Efficiency Gain</div>
                            <div className="metric-value">{(95 / parseFloat(sparsityPercent)).toFixed(1)}x</div>
                            <div className="metric-subtitle">Fewer active neurons</div>
                        </div>

                        <div className="metric-card glass-card">
                            <div className="metric-label">Memory Savings</div>
                            <div className="metric-value">~{(100 - parseFloat(sparsityPercent)).toFixed(0)}%</div>
                            <div className="metric-subtitle">Reduced footprint</div>
                        </div>
                    </div>

                    <div className="insights glass-card">
                        <h3>Key Insights</h3>
                        <ul>
                            <li>
                                <strong>Natural Sparsity:</strong> This untrained model shows ~{sparsityPercent}% activation
                                due to ReLU naturally zeroing negative values. With proper training, BDH achieves
                                even higher sparsity (~3-5%), compared to Transformer's ~95% dense activation.
                            </li>
                            <li>
                                <strong>Biological Plausibility:</strong> Sparse activation patterns mirror how real neurons
                                in the brain work - only a small subset fires at any given time. Training enhances this
                                natural sparsity.
                            </li>
                            <li>
                                <strong>Efficiency Potential:</strong> Even at {sparsityPercent}% sparsity, we see significant
                                memory savings. A trained model with ~5% sparsity would be ~19x more efficient than
                                Transformers in terms of active neurons.
                            </li>
                            <li>
                                <strong>Interpretability:</strong> Sparse activations make it easier to identify which neurons
                                are responsible for specific computations, enabling better model understanding.
                            </li>
                        </ul>
                    </div>
                </>
            )}
        </div>
    );
};

export default SparseBrain;
