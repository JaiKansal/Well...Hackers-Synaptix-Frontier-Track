# 🧠 Sparse Brain Visualization

## Overview
The **Sparse Brain** module visualizes the defining feature of BDH networks: **sparsity**. Unlike Transformers which activate ~95% of neurons for every input, BDH networks only activate a small fraction (3-25%), mimicking biological efficiency.

## What You See
- **Side-by-Side Comparison**: BDH behavior (Left) vs. Transformer behavior (Right).
- **Layer Scrubber**: Detailed interaction to move through the network's depth (Layers 1-12).
- **Heatmap**: 
  - **X-Axis**: Token sequence (Time).
  - **Y-Axis**: Neuron indices.
  - **Color**: Activation intensity (Brighter = Stronger firing).

## Key Metric: 3.9x Efficiency
Our visualization demonstrates that BDH achieves comparable representational power while activating **3.9x fewer neurons**. This has massive implications for:
- **Energy Consumption**: Fewer floating point operations (FLOPs).
- **Interpretability**: Easier to pinpoint "responsible" neurons.
- **Memory Bandwidth**: Less data movement during inference.

## How It Works
1. **Input Sequence**: A sequence of tokens is fed into the backend.
2. **Instrumentation**: We hook into the `BDH` model's forward pass to capture post-activation values.
3. **Thresholding**: The visualization highlights non-zero activations, clearly showing the "dead" (inactive) space that makes BDH efficient.
