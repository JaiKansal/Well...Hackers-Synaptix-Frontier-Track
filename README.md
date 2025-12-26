# BDH Brain Explorer 🧠

**Interactive Visualization & Educational Tool for the Baby Dragon Hatchling Architecture**

Built for the **Synaptix Frontier AI Hackathon - Track 2**

---

## 🎯 Project Overview

BDH Brain Explorer is an interactive web application that visualizes and explains the Baby Dragon Hatchling (BDH) architecture - a post-Transformer breakthrough in AI that works like the brain actually works.

### What Makes BDH Special?

| Property | Transformer | BDH |
|----------|-------------|-----|
| **Structure** | Dense matrices | Scale-free graph |
| **Activation** | ~95% dense | ~5% sparse |
| **Memory** | KV-cache (grows) | Hebbian synapses (constant) |
| **Attention** | O(T²) | O(T) |
| **Interpretability** | Black box | Visualizable |

---

## 🚀 Features (Planned)

### Module 1: Sparse Brain
Side-by-side activation comparison showing BDH's 5% sparsity vs Transformer's 95% density.

### Module 2: Graph Brain
Interactive force-directed graph explorer showing emergent scale-free topology.

### Module 3: Hebbian Animator
Real-time visualization of synapse strengthening ("neurons that fire together, wire together").

### Module 4: Pathfinder Live
Interactive maze-solving demo - draw a maze, watch BDH solve it with live reasoning visualization.

### Module 5: Comparison Tool
BDH vs Transformer metrics dashboard with side-by-side comparison.

---

## 📁 Project Structure

```
bdh-brain-explorer/
├── reference-bdh/              # krychu/bdh implementation
│   ├── bdh.py                  # Core BDH architecture
│   ├── boardpath.py            # Pathfinding task
│   └── utils/                  # Visualization utilities
├── backend/
│   ├── models/
│   │   ├── bdh_instrumented.py # BDH with state tracking
│   │   └── state_extractor.py  # Extract internal states
│   ├── api/
│   │   └── app.py              # FastAPI server
│   └── utils/
├── frontend/
│   └── src/
│       ├── components/         # React components
│       ├── hooks/              # Custom hooks
│       ├── utils/              # Utilities
│       └── styles/             # CSS (glassmorphism)
├── docs/
│   ├── METHODOLOGY.md
│   ├── HYPERPARAMETERS.md
│   └── REPRODUCIBILITY.md
├── demos/gifs/                 # Generated visualizations
├── ARCHITECTURE_NOTES.md       # Architecture deep dive
└── DAY_1_COMPLETE.md          # Day 1 summary
```

---

## 🛠️ Setup

### Backend

```bash
cd reference-bdh
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install torch numpy matplotlib networkx pillow
```

### Frontend (Coming Soon)

```bash
cd frontend
npm install
npm run dev
```

---

## 📊 Current Status

**Day 1 Complete** ✅
- [x] Environment setup
- [x] BDH architecture understood
- [x] Code studied and documented
- [x] Project structure created

**Day 2 In Progress** 🚧
- [ ] BDH instrumentation
- [ ] State extraction utilities
- [ ] Data export for frontend

---

## 🎓 Learn More

### Paper
- [The Dragon Hatchling: The Missing Link between the Transformer and Models of the Brain](https://arxiv.org/abs/2509.26507)

### Resources
- [Official BDH Repository](https://github.com/pathwaycom/bdh)
- [krychu/bdh (Educational Implementation)](https://github.com/krychu/bdh)
- [Pathway BDH Page](https://pathway.com/bdh)

### Inspiration
- [Transformer Explainer](https://poloclub.github.io/transformer-explainer/)
- [LLM Viz](https://bbycroft.net/llm)
- [Colorful Vectors](https://huggingface.co/spaces/jphwang/colorful_vectors)

---

## 🏆 Hackathon Goals

**Target Score**: 100-115 / 120 points

### Judging Criteria
- **Technical Correctness (30)**: Built on validated krychu/bdh code
- **Insight Quality (30)**: Demonstrates all 5 unique BDH properties
- **Creativity (20)**: Novel interactive visualizations
- **Presentation (20)**: Premium UI + professional video
- **Novelty (8)**: Real-time synapse evolution (not in paper)
- **Community Value (7)**: Reusable educational tool
- **Rigor (5)**: Complete methodology documentation

---

## 👥 Team

Built with ❤️ for the Synaptix Frontier AI Hackathon

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🙏 Credits

- Based on [krychu/bdh](https://github.com/krychu/bdh)
- Paper: [The Dragon Hatchling](https://arxiv.org/abs/2509.26507)
- Pathway Team for the BDH architecture

---

**Status**: 🚧 Work in Progress - Day 1 Complete!

**Next Update**: Day 2 - BDH Instrumentation & State Extraction
