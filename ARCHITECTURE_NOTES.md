# BDH Architecture Notes - Day 1 Deep Dive

**Date**: December 26, 2025
**Source**: krychu/bdh implementation
**Paper**: The Dragon Hatchling (arXiv:2509.26507)

---

## Key Equations

### Graph Topologies
```python
# Causal Circuit (how signals propagate between neurons)
Gx = E @ Dx  # [N, D] @ [H, D, N//H] → [N, N]

# Output Circuit (which neurons should fire)
Gy = Dy @ E  # [H, D, N//H] @ [N, D] → [N, N]
```

### Forward Pass (Per Layer)
```python
1. x = ReLU(v_ast @ Dx)                    # Context → Neuron activations
2. a_ast = LinearAttention(x, x, v_ast)    # Self-attention
3. y = ReLU(ln(a_ast) @ Dy) * x            # Output neurons (gated by x)
4. v_ast = v_ast + ln(y @ E)               # Update context
5. v_ast = ln(v_ast)                       # Normalize
```

### Key Insight: No Explicit Sigma in This Implementation
**Important Discovery**: This implementation uses **linear attention** instead of explicit Hebbian sigma matrix!
- Paper version: Uses σ matrix with Hebbian updates
- This version: Uses `LinearAttention` with Q=K=x, V=v_ast
- Both achieve similar effect: context-dependent neuron interactions

---

## Tensor Shapes

For configuration: N=8192, D=512, H=16, T=64, V=100, L=12

| Tensor | Shape | Description |
|--------|-------|-------------|
| `input_` | [B, T] | Input token IDs |
| `v_ast` | [B, 1, T, D] | Context vector (evolves per layer) |
| `x` | [B, H, T, N//H] | Neuron activations (context-dependent) |
| `y` | [B, 1, T, N] | Output neuron activations |
| `E` | [N, D] | Neuron embeddings |
| `Dx` | [H, D, N//H] | Context→Neuron projection |
| `Dy` | [H, D, N//H] | Context→Output projection |
| `readout` | [D, V] | Final projection to vocabulary |
| `logits` | [B, T, V] | Output predictions |

**Notation**:
- B = batch size
- T = sequence length (tokens)
- H = number of heads
- N = total neurons
- N//H = neurons per head
- D = latent dimension
- V = vocabulary size
- L = number of layers

---

## Architecture Components

### 1. Embedding Layer
```python
self.emb = nn.Embedding(V, D)  # Token → D-dimensional embedding
self.pos = nn.Embedding(T, D)  # Optional positional embeddings
```

### 2. Core BDH Matrices
```python
self.E = nn.Parameter(torch.zeros((N, D)).normal_(std=0.02))
self.Dx = nn.Parameter(torch.zeros((H, D, N//H)).normal_(std=0.02))
self.Dy = nn.Parameter(torch.zeros((H, D, N//H)).normal_(std=0.02))
```

**What they do**:
- `E`: Maps each of N neurons to D-dimensional space
- `Dx`: Projects context (D-dim) to neuron activations (N-dim)
- `Dy`: Projects context (D-dim) to output neurons (N-dim)

### 3. Linear Attention
```python
class LinearAttention:
    def forward(self, Q, K, V):
        scores = Q @ K.transpose(-1, -2)  # [B, H, T, T]
        output = scores @ V                # [B, H, T, D]
```

**Key difference from Transformer**:
- Transformer: Softmax attention (normalized)
- BDH: Linear attention (no softmax)
- Both are O(T²) in this implementation, but BDH can be made O(T) with recurrent formulation

### 4. ReLU Activations (Sparse & Positive)
```python
x = F.relu(v_ast @ self.Dx)  # Only positive activations
y = F.relu(ln(a_ast) @ self.Dy) * x  # Gated by x
```

**Why ReLU**:
- Enforces positive-only activations
- Creates natural sparsity (many zeros)
- Prevents polysemantic superposition
- Biologically plausible (neurons don't fire negatively)

---

## Key Properties Observed

### 1. Sparsity
**Claim from README**: "y activations are extremely sparse (~3-5%)"

**Where to measure**:
```python
# In forward pass, after computing y:
y_reshaped = y[0].transpose(0, 1).reshape(T, N)  # [T, N]
sparsity = (y_reshaped != 0).float().mean()  # Should be ~0.03-0.05
```

**Validation needed**: Run inference and measure actual sparsity

### 2. Scale-Free Topology
**Claim from README**: "Sparse, modular organization... spontaneously organized from random initialization"

**Where to extract**:
```python
# Compute Gx matrix
Gx = model.E @ model.Dx  # [N, D] @ [H, D, N//H]
# Need to reshape Dx properly for this to work
```

**Validation needed**: 
- Extract Gx after training
- Compute degree distribution
- Verify power-law (heavy-tailed)

### 3. Emergent Hub Neurons
**Claim from README**: "Neurons ranked by degree... top candidates are hubs"

**How to identify**:
```python
# Compute degree for each neuron
degrees = (abs(Gx) > threshold).sum(dim=1)
hub_threshold = np.percentile(degrees, 90)  # Top 10%
hubs = [i for i, deg in enumerate(degrees) if deg >= hub_threshold]
```

### 4. Attention Flow
**Claim from README**: "Attention radiates from START and END"

**Where captured**:
```python
# In forward pass with capture_frames=True:
attn_scores = self.linear_attn(x, x, v_ast, return_scores=True)
# attn_scores shape: [B, H, T, T]
# Average over heads: attn_scores.mean(dim=1) → [B, T, T]
```

---

## Differences from Paper

### This Implementation (krychu/bdh):
1. **Attention**: Uses `LinearAttention` (Q @ K.T @ V)
2. **No explicit σ**: Attention mechanism replaces Hebbian matrix
3. **Multi-head**: Uses H heads with N//H neurons each
4. **RoPE**: Optional rotary positional embeddings

### Paper Version:
1. **Attention**: Uses explicit σ matrix with Hebbian updates
2. **Hebbian learning**: σ = σ + η(y.T @ y)
3. **Single-head**: Typically uses all N neurons together
4. **Positional**: Absolute or no positional embeddings

### Why the difference?
- This is an **educational implementation** for pathfinding
- Simplified for clarity and GPU efficiency
- Core principles remain: sparse activations, graph structure, neuron-centric

---

## Visualization Opportunities

### 1. Activation Sparsity
**Data**: `y_frames` from `capture_frames=True`
**Visualization**: Heatmap [T, N] showing which neurons fire
**Expected**: ~95% of values should be zero (dark)

### 2. Graph Topology
**Data**: `Gx = E @ Dx` (need to reshape properly)
**Visualization**: Force-directed graph with NetworkX
**Expected**: Hub-and-spoke structure, not random

### 3. Attention Flow
**Data**: `attn_frames` from `capture_frames=True`
**Visualization**: Arrows showing token-to-token attention
**Expected**: Attention from START/END to neighboring cells

### 4. Layer-by-Layer Evolution
**Data**: `output_frames`, `x_frames`, `y_frames`
**Visualization**: Animation showing predictions refining
**Expected**: Path discovered progressively across layers

---

## Questions to Explore

### Answered:
✅ **How are neurons organized?** Multi-head structure with N//H neurons per head
✅ **What creates sparsity?** ReLU activations + natural sparsity from gating
✅ **How is attention computed?** Linear attention (Q @ K.T @ V)

### To Investigate:
❓ **How does Gx topology look?** Need to extract and visualize
❓ **What do hub neurons encode?** Need to analyze activation patterns
❓ **How sparse are activations actually?** Need to measure on real data
❓ **How does this compare to Transformer?** Need side-by-side comparison

---

## Next Steps for Day 2

### 1. Instrument the Model
- [ ] Modify `bdh.py` to expose Gx, Gy matrices
- [ ] Add hooks to capture σ-like information (attention patterns)
- [ ] Save intermediate states for visualization

### 2. Extract Topology
- [ ] Compute Gx properly (handle multi-head structure)
- [ ] Build NetworkX graph
- [ ] Measure degree distribution
- [ ] Identify hub neurons

### 3. Measure Sparsity
- [ ] Run inference with `capture_frames=True`
- [ ] Compute sparsity: `(y != 0).mean()`
- [ ] Verify ~3-5% as claimed
- [ ] Compare x vs y sparsity

### 4. Prepare Data for Frontend
- [ ] Export states to JSON
- [ ] Create test fixtures
- [ ] Document data schemas

---

## Code Snippets for Tomorrow

### Extract Gx Matrix
```python
# After model is loaded
with torch.no_grad():
    # E: [N, D]
    # Dx: [H, D, N//H]
    # Need to reshape for proper multiplication
    
    # Option 1: Per-head Gx
    Gx_per_head = []
    for h in range(model.H):
        Gx_h = model.E @ model.Dx[h]  # [N, D] @ [D, N//H] → [N, N//H]
        Gx_per_head.append(Gx_h)
    
    # Option 2: Combined Gx (concatenate heads)
    # Gx_full = torch.cat(Gx_per_head, dim=1)  # [N, N]
```

### Measure Sparsity
```python
def measure_sparsity(model, input_tokens):
    with torch.no_grad():
        logits, _, x_frames, y_frames, _, _ = model(input_tokens, capture_frames=True)
        
        # Measure y sparsity per layer
        y_sparsity = []
        for y in y_frames:
            sparsity = (y != 0).float().mean().item()
            y_sparsity.append(sparsity)
        
        print(f"Y sparsity per layer: {y_sparsity}")
        print(f"Average Y sparsity: {np.mean(y_sparsity):.4f}")
        
        return y_sparsity
```

### Export for Visualization
```python
def export_states(model, input_tokens, output_path):
    with torch.no_grad():
        logits, output_frames, x_frames, y_frames, attn_frames, _ = \
            model(input_tokens, capture_frames=True)
        
        states = {
            'output_frames': [f.cpu().numpy().tolist() for f in output_frames],
            'x_frames': [f.cpu().numpy().tolist() for f in x_frames],
            'y_frames': [f.cpu().numpy().tolist() for f in y_frames],
            'attn_frames': [f.cpu().numpy().tolist() for f in attn_frames],
            'sparsity': [(y != 0).float().mean().item() for y in y_frames]
        }
        
        with open(output_path, 'w') as f:
            json.dump(states, f)
```

---

## Key Insights from Day 1

1. **BDH is beautifully simple**: Core forward pass is ~40 lines of code
2. **Sparsity comes from ReLU**: No explicit top-k needed (unlike paper)
3. **Multi-head structure**: Similar to Transformer but with neuron-centric view
4. **Visualization-ready**: `capture_frames=True` gives us everything we need
5. **Educational focus**: This implementation prioritizes clarity over paper exactness

---

## Resources Consulted

- [x] krychu/bdh README.md
- [x] krychu/bdh bdh.py (full file)
- [x] krychu/bdh boardpath.py (outline)
- [ ] BDH paper Section 3 (GPU formulation) - TO READ TONIGHT
- [ ] BDH paper Section 6 (Interpretability) - TO READ TONIGHT

---

**End of Day 1 Architecture Notes**

*Tomorrow: Instrument the model and extract visualization data!*
