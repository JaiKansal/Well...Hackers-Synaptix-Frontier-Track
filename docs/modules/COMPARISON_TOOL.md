# 📊 Model Comparison Tool

## Overview
Science requires benchmarking. The Comparison Tool provides hard data comparing our **BDH Implementation** against a standard **PyTorch Transformer** of equivalent size.

## Metrics Tracked
We track four critical dimensions of performance:

| Metric | BDH Advantage | Description |
|--------|--------------|-------------|
| **Sparsity** | **High** (~25%) | Percentage of inactive neurons. Higher sparsity = better efficiency. |
| **Model Size** | **Neutral** | Same parameter count ($O(N^2)$), but effective size is smaller due to sparsity. |
| **Inference Time** | **Variable** | BDH requires specialized sparse kernels to beat dense matrix multiplication on modern GPUs. |
| **Memory Footprint** | **High** | Lower active memory usage during forward pass. |

## Interactive Benchmarking
Unlike static tables in papers, this tool runs **live benchmarks**:
1. Click "Run Benchmark".
2. The backend instantiates both models.
3. Random batches of data are fed through both.
4. Timers and memory profilers capture real execution stats.

## Interpretation
- **Green Bars**: BDH wins.
- **Blue Bars**: Transformer wins.
- **Key Insight**: While Transformers (highly optimized by NVIDIA/PyTorch) may win on raw raw speed currently, BDH wins on **efficiency per computation** and **interpretability**.
