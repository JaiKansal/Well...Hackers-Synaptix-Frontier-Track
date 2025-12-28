# ⚡ Hebbian Learning Animator

## The Concept
*"Neurons that fire together, wire together."*
This is the fundamental rule of biological learning, and it's central to BDH. Unlike backpropagation which is a global optimization, Hebbian learning is **local** and **unsupervised**.

## Visualization Explained
This module animates the training process itself:
1. **Initial State**: Weak, random connections (thin grey lines).
2. **Co-Activation**: When two neurons fire simultaneously (flashing).
3. **Weight Update**: The connection between them grows thicker and changes color (Gold/Green).
4. **Decay (LTD)**: Unused connections slowly fade away (Long-Term Depression).

## Why It Matters
This visualization proves that BDH is **learning structures**, not just memorizing. You can literally watch the network discover features:
- **Feature Clusters**: Groups of neurons that learn to respond to related concepts.
- **Sequence Chains**: A → B → C firing patterns engaging.

## Controls
- **Play/Pause**: Stop the learning process to inspect the current state.
- **Speed Control**: Slow down time to see micro-updates or speed up to see global convergence.
- **Reset**: Re-initialize weights to random values.
