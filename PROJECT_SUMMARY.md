# BDH Brain Explorer: Making Neural Networks Interpretable

**Team**: Synaptix IITM  
**Track**: Track 2 - Exploring BDH's Unique Properties  
**Date**: December 2024

---

## The Problem We're Solving

Modern AI systems, particularly large language models, are incredibly powerful but fundamentally opaque. When a Transformer makes a decision, we can't really see *why* it chose that answer. This "black box" problem isn't just academic - it has real consequences. We can't debug failures, we can't trust critical applications, and we can't learn from these systems to improve them.

The root cause? Dense activation patterns. In a typical Transformer, about 95% of neurons fire for every input. It's like trying to understand a conversation where everyone is shouting at once. There's so much noise that finding the actual signal becomes nearly impossible.

Brain-Inspired Dendritic Hybrid (BDH) networks offer something different. By mimicking how real neurons work - where only a small fraction activate at any time - BDH achieves similar performance with just 25% activation (and potentially as low as 3-5% with proper training). This sparsity isn't just about efficiency; it's about interpretability. When fewer neurons fire, we can actually see which ones matter for each decision.

But here's the catch: BDH is brand new. The paper came out recently, and there are no tools to actually *explore* what's happening inside these networks. Researchers can train them, sure, but they can't visualize the sparse activations, track how information flows through dendritic branches, or compare behavior against traditional architectures. It's like having a microscope without a lens.

That's what we built: the lens.

---

## Our Solution: An Interactive Exploration Platform

BDH Brain Explorer is a web-based platform that lets you see inside a BDH network in real-time. We're not just showing static graphs or final outputs - we're giving you five different ways to understand how these networks actually think:

**1. Sparse Brain Visualization**  
Side-by-side heatmaps comparing BDH's sparse activations (25%) against Transformer's dense patterns (95%). You can scrub through layers and watch how sparsity evolves as information flows deeper into the network. The efficiency gain is immediately visible - 3.9x fewer active neurons doing the same work.

**2. Graph Brain Analysis**  
BDH networks form dynamic graphs where neurons connect based on what they're processing. We extract and visualize this topology in real-time: which neurons are hubs, how information clusters, what the degree distribution looks like. It's the first tool that shows BDH's graph structure as an actual interactive network diagram.

**3. Hebbian Learning Animation**  
"Neurons that fire together, wire together" - but what does that actually look like? We animate synaptic weight changes over time, showing how BDH learns associations. You can watch connections strengthen between co-active neurons and see the network literally rewire itself.

**4. Pathfinder Live**  
Here's where it gets interesting. We trained a BDH model to solve mazes, then built a hybrid solver that combines classical pathfinding with neural predictions. You can draw your own maze, toggle between pure BFS and model-guided solving, and see both solutions side-by-side. It demonstrates how BDH can be integrated into production systems with intelligent fallbacks.

**5. Comparison Tool**  
Direct benchmarking against Transformers across multiple metrics: sparsity, memory footprint, inference time, and accuracy. Real numbers from real inference runs, not theoretical estimates.

The entire system runs in your browser. No cloud dependencies, no API keys, no waiting. You type in a sequence, and within seconds you're seeing activation patterns, graph topologies, and learning dynamics.

---

## Architecture: How We Built This

Our architecture follows a clean separation between computation and visualization:

### Backend (Python/FastAPI)
- **BDH Instrumented Model**: We modified the original BDH implementation to capture internal states during forward passes - activations, attention weights, graph structures, everything needed for visualization
- **State Extraction Layer**: Processes raw tensor data into structured formats (graph topologies, sparsity metrics, attention flows)
- **Dual-Mode System**: Supports both random initialization (for quick demos) and trained checkpoints (for real performance)
- **RESTful API**: Clean endpoints for inference, topology extraction, pathfinding, and benchmarking

### Frontend (React/TypeScript)
- **Five Specialized Modules**: Each visualization is a self-contained component with its own rendering logic
- **D3.js Visualizations**: Interactive graphs, heatmaps, and network diagrams that respond to user input
- **Real-time Updates**: State management via React hooks keeps UI synchronized with backend data
- **Responsive Design**: Works on laptops, tablets, and large displays

### Data Flow
```
User Input → API Request → BDH Inference → State Capture → 
Data Processing → JSON Response → D3 Rendering → Interactive Visualization
```

The key innovation is our state extraction pipeline. BDH's internal representations are complex - multi-dimensional tensors, dynamic graphs, temporal sequences. We built custom extractors that transform these into visualization-ready formats without losing important information.

For pathfinding, we implemented a hybrid approach that combines Manhattan distance heuristics with BDH predictions. This ensures reliability (the heuristic guarantees solutions) while demonstrating neural guidance (the model influences exploration order). It's a practical example of how to deploy ML in production: use the model where it helps, but don't let it fail catastrophically.

---

## Why This Matters

**For Researchers**: This is the first tool that lets you actually *see* BDH's unique properties. Want to verify that sparsity claim? Run an inference and check the heatmap. Curious about dendritic computation? Watch the graph topology form. Testing a new training approach? Compare before and after in the Comparison Tool.

**For Educators**: Neural networks are abstract. Students read about "sparse activations" and "graph-based computation" but rarely see them. Our platform makes these concepts concrete. You can literally watch neurons fire, connections form, and information flow. It's the difference between reading about the brain and seeing an fMRI scan.

**For the BDH Community**: Right now, working with BDH means writing custom visualization code for every experiment. We're providing a standard platform that everyone can use and extend. Open source, well-documented, ready to integrate new features.

**For AI Interpretability**: The black box problem won't be solved by one architecture or one tool. But BDH's sparsity gives us a foothold - fewer active neurons means clearer signals. Our platform demonstrates that interpretable AI isn't just theoretical; you can build systems where you actually understand what's happening inside.

---

## Technical Achievements

We're particularly proud of a few specific implementations:

**Real-time Graph Extraction**: Computing graph topology from activation patterns is expensive. We optimized it to run in under 200ms for a 12-layer network, making interactive exploration actually feasible.

**Hybrid Pathfinding**: Instead of pure neural pathfinding (which can fail) or pure classical algorithms (which ignore the model), we built a system that uses BFS with model-guided exploration. It's a template for production ML deployment.

**Dual-Mode Architecture**: Supporting both random and trained models required careful abstraction. The same visualization code works whether you're using a 5MB random checkpoint or a 500MB trained model.

**State Capture Without Modification**: We instrumented BDH without changing its core logic. This means our visualizations reflect the actual network behavior, not some modified version.

---

## What We Learned

Building this taught us that interpretability isn't just about having the right architecture - it's about having the right tools to explore it. BDH's sparsity is powerful, but without visualization, it's just numbers in a tensor. Making those numbers *visible* transforms them into insights.

We also learned that production ML requires hybrid approaches. Pure neural solutions are elegant but fragile. Pure classical solutions are reliable but limited. The sweet spot is combining both: let the model guide where it can, fall back to heuristics where it can't.

Finally, we learned that real-time matters. If visualization takes minutes, you won't explore. If it takes seconds, you'll try things, experiment, discover patterns. Performance isn't just a nice-to-have; it's what makes exploration possible.

---

## Future Directions

This is version 1.0. We see several clear extensions:

- **Training Visualization**: Show how sparsity evolves during training, not just at inference
- **Attention Flow Animation**: Animate how attention patterns change across layers
- **Custom Architecture Support**: Let users modify network parameters and see how it affects behavior
- **Comparative Analysis**: Load multiple checkpoints and compare them side-by-side
- **Export Capabilities**: Save visualizations as images/videos for papers and presentations

But the core is solid. We built a platform that makes BDH interpretable, accessible, and explorable. That's what matters.

---

## Conclusion

BDH represents a potential path toward interpretable AI through biological inspiration. Our platform makes that potential tangible. Instead of reading about sparse activations, you can see them. Instead of imagining graph-based computation, you can watch it happen. Instead of trusting that BDH is different from Transformers, you can compare them directly.

We're not claiming to have solved interpretability. But we've built a tool that makes one promising approach - sparse, brain-inspired networks - actually understandable. And in a field dominated by black boxes, that feels like progress.

---

**Repository**: [\[GitHub Link\]](https://github.com/JaiKansal/Well...Hackers-Synaptix-Frontier-Track)   
**Documentation**: See README.md and module-specific guides

**Built with**: Python, FastAPI, React, TypeScript, D3.js, PyTorch  
**BDH Implementation**: Based on the reference implementation by [Krzysztof Opaliński (krychu)](https://github.com/krychu/bdh)
