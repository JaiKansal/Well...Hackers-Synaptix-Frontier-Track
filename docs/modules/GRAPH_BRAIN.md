# 🕸️ Graph Brain Analysis

## Overview
BDH networks are not just stacked layers; they form dynamic **graph topologies**. Neurons connect based on correlation and signal strength. This module extracts and visualizes this hidden structure in real-time.

## Features
- **Force-Directed Graph**: An interactive D3.js visualization where nodes repel and correlated links attract.
- **Hub Detection**: Large nodes represent "Hub Neurons" - widely connected units essential for information flow.
- **Dynamic Topology**: As you change inputs, watch the graph reorganize itself (Hebbian rewiring).

## Technical Implementation
### Graph Extraction Algorithm
Extracting a graph from a tensor is non-trivial. We use the following approach:
1. **Correlation Matrix**: Calculate the Pearson correlation coefficient between neuron activation vectors across the batch.
2. **Thresholding**: Links are only created if correlation > `0.7` (configurable).
3. **Optimized JSON**: The backend sends a simplified Node/Link list to the frontend to maintain 60FPS performance.

## Usage
- **Drag Nodes**: You can physically grab and move neurons to disentangle clusters.
- **Hover**: See specific neuron IDs and their current degree (connection count).
- **Zoom/Pan**: Explore large-scale structures efficiently.
