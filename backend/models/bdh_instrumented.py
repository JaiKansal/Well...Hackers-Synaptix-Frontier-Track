"""
BDH Instrumented Model - Extended version with state tracking for visualization

This module extends the base BDH implementation from krychu/bdh to capture
internal states for visualization purposes.

Key additions:
- Gx, Gy matrix extraction
- Sparsity measurements
- Attention pattern tracking
- Per-layer state capture
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../reference-bdh'))

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple, Optional
from bdh import BDH, BDHParameters


class BDHInstrumented(BDH):
    """
    Extended BDH model with instrumentation for visualization.
    
    Inherits from base BDH and adds:
    - State tracking hooks
    - Graph topology extraction
    - Sparsity measurements
    - Attention pattern capture
    """
    
    def __init__(self, params: BDHParameters):
        super().__init__(params)
        
        # State tracking
        self.tracking_enabled = False
        self.states = self._init_states()
        
    def _init_states(self) -> Dict:
        """Initialize state tracking dictionary"""
        return {
            'y_activations': [],       # Neuron activations per layer [L, T, N]
            'x_activations': [],       # Context activations per layer [L, T, N]
            'attention_weights': [],   # Attention patterns [L, T, T]
            'output_frames': [],       # Predictions per layer [L, T]
            'logits_frames': [],       # Logits per layer [L, T, V]
            'sparsity_per_layer': [],  # Sparsity measurements [L]
            'Gx_topology': None,       # Causal circuit graph [N, N]
            'Gy_topology': None,       # Output circuit graph [N, N]
            'layer_norms': [],         # Layer normalization stats
        }
    
    def enable_tracking(self):
        """Enable state tracking for next forward pass"""
        self.tracking_enabled = True
        self.states = self._init_states()
    
    def disable_tracking(self):
        """Disable state tracking"""
        self.tracking_enabled = False
    
    def get_states(self) -> Dict:
        """Return captured states"""
        return self.states
    
    def extract_graph_topologies(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract Gx and Gy graph topologies.
        
        Returns:
            Gx: Causal circuit [N, N]
            Gy: Output circuit [N, N]
        """
        with torch.no_grad():
            # E: [N, D]
            # Dx: [H, D, N//H]
            # Dy: [H, D, N//H]
            
            H, D, Nh = self.Dx.shape
            N = self.N
            
            # Compute Gx = E @ Dx for each head, then combine
            Gx_heads = []
            Gy_heads = []
            
            for h in range(H):
                # Gx_h = E @ Dx[h]  # [N, D] @ [D, N//H] -> [N, N//H]
                Gx_h = self.E @ self.Dx[h]
                Gx_heads.append(Gx_h)
                
                # Gy_h = Dy[h].T @ E.T  # [D, N//H].T @ [N, D].T -> [N//H, D] @ [D, N] -> [N//H, N]
                Gy_h = self.Dy[h].T @ self.E.T
                Gy_heads.append(Gy_h)
            
            # Concatenate heads: [N, H * N//H] = [N, N]
            Gx = torch.cat(Gx_heads, dim=1).cpu().numpy()
            
            # For Gy, we need to transpose and concatenate differently
            # Each Gy_h is [N//H, N], stack them to get [H * N//H, N] = [N, N]
            Gy = torch.cat(Gy_heads, dim=0).cpu().numpy()
            
            return Gx, Gy
    
    def forward(self, input_, capture_frames=False):
        """
        Forward pass with optional state tracking.
        
        Args:
            input_: Input token IDs [B, T]
            capture_frames: If True, capture internal states
        
        Returns:
            If capture_frames=False: logits [B, T, V]
            If capture_frames=True: (logits, output_frames, x_frames, y_frames, attn_frames, logits_frames)
        """
        # If tracking is enabled, force capture_frames
        if self.tracking_enabled:
            capture_frames = True
        
        # Call parent forward pass
        if capture_frames:
            result = super().forward(input_, capture_frames=True)
            logits, output_frames, x_frames, y_frames, attn_frames, logits_frames = result
            
            # If tracking enabled, store states
            if self.tracking_enabled:
                self._store_states(output_frames, x_frames, y_frames, attn_frames, logits_frames)
            
            return result
        else:
            return super().forward(input_, capture_frames=False)
    
    def _store_states(self, output_frames, x_frames, y_frames, attn_frames, logits_frames):
        """Store captured states in tracking dictionary"""
        # Convert to numpy and store
        self.states['output_frames'] = [f.cpu().numpy() for f in output_frames]
        self.states['x_activations'] = [f.cpu().numpy() for f in x_frames]
        self.states['y_activations'] = [f.cpu().numpy() for f in y_frames]
        self.states['attention_weights'] = [f.cpu().numpy() for f in attn_frames]
        self.states['logits_frames'] = [f.cpu().numpy() for f in logits_frames]
        
        # Compute sparsity per layer
        for y in y_frames:
            sparsity = (y != 0).float().mean().item()
            self.states['sparsity_per_layer'].append(sparsity)
        
        # Extract graph topologies
        Gx, Gy = self.extract_graph_topologies()
        self.states['Gx_topology'] = Gx
        self.states['Gy_topology'] = Gy
    
    def measure_sparsity(self, input_tokens: torch.Tensor) -> Dict[str, float]:
        """
        Measure activation sparsity on given input.
        
        Args:
            input_tokens: Input token IDs [B, T]
        
        Returns:
            Dictionary with sparsity metrics
        """
        self.eval()
        with torch.no_grad():
            self.enable_tracking()
            _ = self.forward(input_tokens, capture_frames=True)
            self.disable_tracking()
            
            states = self.get_states()
            
            # Compute statistics
            y_sparsity = states['sparsity_per_layer']
            
            # Compute x sparsity
            x_sparsity = []
            for x in states['x_activations']:
                sparsity = (x != 0).mean()
                x_sparsity.append(float(sparsity))
            
            return {
                'y_sparsity_mean': float(np.mean(y_sparsity)),
                'y_sparsity_std': float(np.std(y_sparsity)),
                'y_sparsity_min': float(np.min(y_sparsity)),
                'y_sparsity_max': float(np.max(y_sparsity)),
                'y_sparsity_per_layer': y_sparsity,
                'x_sparsity_mean': float(np.mean(x_sparsity)),
                'x_sparsity_std': float(np.std(x_sparsity)),
                'x_sparsity_per_layer': x_sparsity,
            }
    
    def get_topology_metrics(self, threshold: float = 0.1) -> Dict:
        """
        Compute graph topology metrics.
        
        Args:
            threshold: Edge weight threshold for topology analysis
        
        Returns:
            Dictionary with topology metrics
        """
        Gx, Gy = self.extract_graph_topologies()
        
        # Compute degree distribution for Gx
        Gx_binary = (np.abs(Gx) > threshold).astype(int)
        degrees = Gx_binary.sum(axis=1)
        
        # Identify hub neurons (top 10%)
        hub_threshold = np.percentile(degrees, 90)
        hubs = np.where(degrees >= hub_threshold)[0].tolist()
        
        # Compute statistics
        return {
            'num_neurons': int(self.N),
            'num_edges': int(Gx_binary.sum()),
            'avg_degree': float(degrees.mean()),
            'max_degree': int(degrees.max()),
            'min_degree': int(degrees.min()),
            'std_degree': float(degrees.std()),
            'hub_threshold': float(hub_threshold),
            'num_hubs': len(hubs),
            'hub_indices': hubs,
            'degree_distribution': degrees.tolist(),
        }
    
    def export_states_for_visualization(self, output_path: str):
        """
        Export captured states to JSON for frontend visualization.
        
        Args:
            output_path: Path to save JSON file
        """
        import json
        
        states = self.get_states()
        
        # Helper function to convert numpy arrays to lists recursively
        def convert_to_list(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, list):
                return [convert_to_list(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: convert_to_list(value) for key, value in obj.items()}
            else:
                return obj
        
        # Convert numpy arrays to lists for JSON serialization
        export_data = {
            'output_frames': convert_to_list(states['output_frames']),
            'x_activations': convert_to_list(states['x_activations']),
            'y_activations': convert_to_list(states['y_activations']),
            'attention_weights': convert_to_list(states['attention_weights']),
            'logits_frames': convert_to_list(states['logits_frames']),
            'sparsity_per_layer': states['sparsity_per_layer'],
            'Gx_topology': states['Gx_topology'].tolist() if states['Gx_topology'] is not None else None,
            'Gy_topology': states['Gy_topology'].tolist() if states['Gy_topology'] is not None else None,
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f)
        
        print(f"States exported to {output_path}")


def load_instrumented_bdh(checkpoint_path: str, device='cpu') -> Tuple[BDHInstrumented, Dict]:
    """
    Load a trained BDH model and wrap it with instrumentation.
    
    Args:
        checkpoint_path: Path to trained model checkpoint
        device: Device to load model on
    
    Returns:
        Instrumented model and config dictionary
    """
    # Load checkpoint
    ckpt = torch.load(checkpoint_path, map_location=device)
    
    # Extract parameters
    bdh_params = BDHParameters(**ckpt['bdh_params_dict'])
    boardpath_params = ckpt.get('boardpath_params_dict', {})
    
    # Create instrumented model
    model = BDHInstrumented(bdh_params)
    model.load_state_dict(ckpt['bdh_state_dict'])
    model.to(device)
    model.eval()
    
    config = {
        'bdh_params': bdh_params,
        'boardpath_params': boardpath_params,
    }
    
    return model, config


if __name__ == '__main__':
    """Test instrumentation"""
    print("Testing BDH Instrumentation...")
    
    # Create a small test model
    params = BDHParameters(
        V=5,
        T=100,
        H=4,
        N=2048,
        D=64,
        L=12,
        dropout=0.1,
        use_rope=True,
        use_abs_pos=False
    )
    
    model = BDHInstrumented(params)
    
    # Test forward pass with tracking
    input_tokens = torch.randint(0, 5, (1, 100))
    
    print("\n1. Testing forward pass with tracking...")
    model.enable_tracking()
    logits, output_frames, x_frames, y_frames, attn_frames, logits_frames = model(input_tokens, capture_frames=True)
    
    print(f"   Logits shape: {logits.shape}")
    print(f"   Captured {len(output_frames)} layers")
    print(f"   Y frames shape: {y_frames[0].shape}")
    
    # Test sparsity measurement
    print("\n2. Testing sparsity measurement...")
    sparsity_metrics = model.measure_sparsity(input_tokens)
    print(f"   Y sparsity mean: {sparsity_metrics['y_sparsity_mean']:.4f}")
    print(f"   Y sparsity std: {sparsity_metrics['y_sparsity_std']:.4f}")
    print(f"   X sparsity mean: {sparsity_metrics['x_sparsity_mean']:.4f}")
    
    # Test topology extraction
    print("\n3. Testing topology extraction...")
    topology_metrics = model.get_topology_metrics(threshold=0.1)
    print(f"   Num neurons: {topology_metrics['num_neurons']}")
    print(f"   Num edges: {topology_metrics['num_edges']}")
    print(f"   Avg degree: {topology_metrics['avg_degree']:.2f}")
    print(f"   Max degree: {topology_metrics['max_degree']}")
    print(f"   Num hubs: {topology_metrics['num_hubs']}")
    
    print("\n✅ All tests passed!")
