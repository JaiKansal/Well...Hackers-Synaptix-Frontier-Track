/**
 * Graph Brain Component
 * 
 * Visualizes BDH's scale-free topology using D3.js force-directed graph
 * Shows hub neurons, degree distribution, and emergent network structure
 */

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { useTopology } from '../hooks/useBDH';
import './GraphBrain.css';

interface GraphBrainProps {
    threshold?: number;
    topKNodes?: number;
}

const GraphBrain: React.FC<GraphBrainProps> = ({
    threshold = 0.01,  // Optimized for trained model (gives ~16k edges)
    topKNodes = 100
}) => {
    const svgRef = useRef<SVGSVGElement>(null);
    const { data, loading, error } = useTopology(threshold, topKNodes);
    const [selectedNode, setSelectedNode] = useState<number | null>(null);
    const [showDegreeChart, setShowDegreeChart] = useState(true);

    useEffect(() => {
        if (!data || !svgRef.current) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();

        const width = 800;
        const height = 600;
        const margin = { top: 20, right: 20, bottom: 20, left: 20 };

        // Create main group
        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // Prepare data
        const nodes = data.nodes.map(n => ({ ...n }));
        const links = data.edges.map(e => ({ ...e }));

        // Color scale based on degree
        const maxDegree = d3.max(nodes, n => n.degree) || 1;
        const colorScale = d3.scaleSequential(d3.interpolateTurbo)
            .domain([0, maxDegree]);

        // Size scale for nodes
        const sizeScale = d3.scaleLinear()
            .domain([0, maxDegree])
            .range([4, 20]);


        // Create force simulation with improved spacing
        const simulation = d3.forceSimulation(nodes as any)
            .force('link', d3.forceLink(links as any)
                .id((d: any) => d.id)
                .distance(100)  // Increased from 50 to spread nodes apart
                .strength(0.3))  // Reduced from 0.5 to make links more flexible
            .force('charge', d3.forceManyBody()
                .strength(-300))  // Increased repulsion from -100 to -300
            .force('center', d3.forceCenter(
                (width - margin.left - margin.right) / 2,
                (height - margin.top - margin.bottom) / 2
            ))
            .force('collision', d3.forceCollide()
                .radius((d: any) => sizeScale(d.degree) + 15))  // Increased padding from 2 to 15
            .alphaDecay(0.02);  // Slower cooling for better settling

        // Create links
        const link = g.append('g')
            .selectAll('line')
            .data(links)
            .join('line')
            .attr('class', 'graph-link')
            .attr('stroke', '#475569')
            .attr('stroke-opacity', 0.3)
            .attr('stroke-width', (d: any) => Math.abs(d.weight) * 2);

        // Create nodes
        const node = g.append('g')
            .selectAll('circle')
            .data(nodes)
            .join('circle')
            .attr('class', 'graph-node')
            .attr('r', (d: any) => sizeScale(d.degree))
            .attr('fill', (d: any) => d.is_hub ? '#f59e0b' : colorScale(d.degree))
            .attr('stroke', '#fff')
            .attr('stroke-width', 2)
            .style('cursor', 'pointer')
            .on('click', (event, d: any) => {
                setSelectedNode(d.id);
                event.stopPropagation();
            })
            .on('mouseover', function (_event, d: any) {
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr('r', sizeScale(d.degree) * 1.5)
                    .attr('stroke-width', 3);

                // Highlight connected links
                link
                    .attr('stroke-opacity', (l: any) =>
                        l.source.id === d.id || l.target.id === d.id ? 0.8 : 0.1
                    )
                    .attr('stroke-width', (l: any) =>
                        l.source.id === d.id || l.target.id === d.id ? 3 : 1
                    );
            })
            .on('mouseout', function (_event, d: any) {
                d3.select(this)
                    .transition()
                    .duration(200)
                    .attr('r', sizeScale(d.degree))
                    .attr('stroke-width', 2);

                // Reset links
                link
                    .attr('stroke-opacity', 0.3)
                    .attr('stroke-width', (l: any) => Math.abs(l.weight) * 2);
            })
            .call(d3.drag<any, any>()
                .on('start', (event, d: any) => {
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                })
                .on('drag', (event, d: any) => {
                    d.fx = event.x;
                    d.fy = event.y;
                })
                .on('end', (event, d: any) => {
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }));


        // Add labels for hub nodes with backgrounds
        const labelGroup = g.append('g')
            .selectAll('g')
            .data(nodes.filter((n: any) => n.is_hub))
            .join('g')
            .attr('class', 'hub-label-group');

        // Add background rectangles for labels
        labelGroup.append('rect')
            .attr('class', 'label-bg')
            .attr('x', -25)
            .attr('y', -28)
            .attr('width', 50)
            .attr('height', 14)
            .attr('rx', 3)
            .attr('fill', 'rgba(15, 23, 42, 0.9)')
            .attr('stroke', '#f59e0b')
            .attr('stroke-width', 1);

        // Add text labels
        labelGroup.append('text')
            .attr('class', 'node-label')
            .attr('text-anchor', 'middle')
            .attr('dy', -17)
            .attr('fill', '#f59e0b')
            .attr('font-size', '9px')
            .attr('font-weight', 'bold')
            .text((d: any) => `Hub ${d.id}`);



        // Update positions on tick
        simulation.on('tick', () => {
            link
                .attr('x1', (d: any) => d.source.x)
                .attr('y1', (d: any) => d.source.y)
                .attr('x2', (d: any) => d.target.x)
                .attr('y2', (d: any) => d.target.y);

            node
                .attr('cx', (d: any) => d.x)
                .attr('cy', (d: any) => d.y);

            // Move entire label group (background + text together)
            labelGroup
                .attr('transform', (d: any) => `translate(${d.x},${d.y})`);
        });

        // Add zoom behavior
        const zoom = d3.zoom<SVGSVGElement, unknown>()
            .scaleExtent([0.5, 5])
            .on('zoom', (event) => {
                g.attr('transform', event.transform);
            });

        svg.call(zoom as any);

        // Cleanup
        return () => {
            simulation.stop();
        };
    }, [data]);

    // Render degree distribution chart
    useEffect(() => {
        if (!data || !showDegreeChart) return;

        const chartSvg = d3.select('#degree-chart');
        chartSvg.selectAll('*').remove();

        const width = 400;
        const height = 200;
        const margin = { top: 20, right: 20, bottom: 40, left: 50 };

        // Get degree distribution from metrics
        const degrees = data.metrics.degree_distribution;

        // Validate degrees is an array with data
        if (!degrees || !Array.isArray(degrees) || degrees.length === 0) {
            console.warn('Invalid or empty degree distribution data:', degrees);
            // Show message in chart area
            chartSvg.append('text')
                .attr('x', width / 2)
                .attr('y', height / 2)
                .attr('text-anchor', 'middle')
                .attr('fill', '#94a3b8')
                .attr('font-size', '14px')
                .text('No degree distribution data available');
            return;
        }

        console.log('Degree distribution:', degrees.slice(0, 10), '... (showing first 10)');

        // Create histogram bins
        const maxDegree = d3.max(degrees) || 100;
        const bins = d3.bin()
            .domain([0, maxDegree])
            .thresholds(20)(degrees);

        const x = d3.scaleLinear()
            .domain([0, maxDegree])
            .range([margin.left, width - margin.right]);

        const y = d3.scaleLinear()
            .domain([0, d3.max(bins, d => d.length) || 10])
            .range([height - margin.bottom, margin.top]);

        // Draw bars
        chartSvg.append('g')
            .selectAll('rect')
            .data(bins)
            .join('rect')
            .attr('x', d => x(d.x0 || 0) + 1)
            .attr('y', d => y(d.length))
            .attr('width', d => Math.max(0, x(d.x1 || 0) - x(d.x0 || 0) - 2))
            .attr('height', d => y(0) - y(d.length))
            .attr('fill', '#6366f1')
            .attr('opacity', 0)
            .transition()
            .duration(500)
            .delay((_, i) => i * 20)
            .attr('opacity', 0.8);

        // Add axes
        chartSvg.append('g')
            .attr('transform', `translate(0,${height - margin.bottom})`)
            .call(d3.axisBottom(x).ticks(5))
            .attr('color', '#94a3b8');

        chartSvg.append('g')
            .attr('transform', `translate(${margin.left},0)`)
            .call(d3.axisLeft(y).ticks(5))
            .attr('color', '#94a3b8');

        // Labels
        chartSvg.append('text')
            .attr('x', width / 2)
            .attr('y', height - 5)
            .attr('text-anchor', 'middle')
            .attr('fill', '#cbd5e1')
            .attr('font-size', '12px')
            .text('Degree');

        chartSvg.append('text')
            .attr('transform', 'rotate(-90)')
            .attr('x', -height / 2)
            .attr('y', 15)
            .attr('text-anchor', 'middle')
            .attr('fill', '#cbd5e1')
            .attr('font-size', '12px')
            .text('Count');

    }, [data, showDegreeChart]);

    const selectedNodeData = selectedNode !== null
        ? data?.nodes.find(n => n.id === selectedNode)
        : null;

    return (
        <div className="graph-brain-container glass-card">
            <div className="graph-brain-header">
                <h2>Graph Brain: Scale-Free Topology</h2>
                <p className="text-muted">
                    BDH's emergent network structure with hub neurons and modular organization
                </p>
            </div>

            {loading && (
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Loading graph topology...</p>
                </div>
            )}

            {error && (
                <div className="error-container">
                    <p className="error-message">Error: {error}</p>
                </div>
            )}

            {data && (
                <>
                    <div className="graph-controls">
                        <button
                            className={`btn ${showDegreeChart ? 'btn-primary' : 'btn-secondary'}`}
                            onClick={() => setShowDegreeChart(!showDegreeChart)}
                        >
                            {showDegreeChart ? 'Hide' : 'Show'} Degree Distribution
                        </button>
                    </div>

                    <div className="graph-visualization">
                        <svg
                            ref={svgRef}
                            width="800"
                            height="600"
                            className="graph-svg"
                        />
                    </div>

                    {showDegreeChart && (
                        <div className="degree-chart-container glass-card">
                            <h3>Degree Distribution</h3>
                            <p className="text-muted">Power-law distribution indicates scale-free network</p>
                            <svg id="degree-chart" width="400" height="200" />
                        </div>
                    )}

                    <div className="metrics-grid">
                        <div className="metric-card glass-card">
                            <div className="metric-label">Total Neurons</div>
                            <div className="metric-value">{data.metrics.num_neurons}</div>
                            <div className="metric-subtitle">Network size</div>
                        </div>

                        <div className="metric-card glass-card">
                            <div className="metric-label">Connections</div>
                            <div className="metric-value">{data.metrics.num_edges}</div>
                            <div className="metric-subtitle">Total edges</div>
                        </div>

                        <div className="metric-card glass-card">
                            <div className="metric-label">Hub Neurons</div>
                            <div className="metric-value">{data.metrics.num_hubs}</div>
                            <div className="metric-subtitle">Highly connected</div>
                        </div>

                        <div className="metric-card glass-card">
                            <div className="metric-label">Avg Degree</div>
                            <div className="metric-value">{data.metrics.avg_degree.toFixed(1)}</div>
                            <div className="metric-subtitle">Connections per neuron</div>
                        </div>
                    </div>

                    {selectedNodeData && (
                        <div className="node-details glass-card">
                            <h3>Neuron {selectedNodeData.id}</h3>
                            <div className="node-stats">
                                <div className="stat">
                                    <span className="stat-label">Total Degree:</span>
                                    <span className="stat-value">{selectedNodeData.degree}</span>
                                </div>
                                <div className="stat">
                                    <span className="stat-label">Incoming:</span>
                                    <span className="stat-value">{selectedNodeData.in_degree}</span>
                                </div>
                                <div className="stat">
                                    <span className="stat-label">Outgoing:</span>
                                    <span className="stat-value">{selectedNodeData.out_degree}</span>
                                </div>
                                <div className="stat">
                                    <span className="stat-label">Hub Status:</span>
                                    <span className={`stat-value ${selectedNodeData.is_hub ? 'hub' : ''}`}>
                                        {selectedNodeData.is_hub ? '⭐ Hub Neuron' : 'Regular'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    )}

                    <div className="insights glass-card">
                        <h3>Key Insights</h3>
                        <ul>
                            <li>
                                <strong>Scale-Free Topology:</strong> The network exhibits a power-law degree distribution,
                                with a few highly connected hub neurons and many sparsely connected nodes.
                            </li>
                            <li>
                                <strong>Emergent Structure:</strong> This organization wasn't hard-coded - it emerged
                                naturally during training, similar to biological neural networks.
                            </li>
                            <li>
                                <strong>Hub Neurons:</strong> The {data.metrics.num_hubs} hub neurons (shown in gold) act as
                                information routing centers, enabling efficient communication across the network.
                            </li>
                            <li>
                                <strong>Modularity:</strong> The network shows modular organization with distinct clusters,
                                each potentially encoding different concepts or functions.
                            </li>
                        </ul>
                    </div>
                </>
            )}
        </div>
    );
};

export default GraphBrain;
