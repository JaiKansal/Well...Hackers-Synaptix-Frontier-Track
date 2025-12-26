"""
State Extraction Utilities for BDH Visualization

This module provides utilities to extract and process BDH internal states
for visualization purposes.
"""

import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class StateExtractor:
    """Extract and process BDH internal states for visualization"""
    
    @staticmethod
    def extract_graph_topology(
        Gx: np.ndarray,
        threshold: float = 0.1,
        top_k_nodes: Optional[int] = None
    ) -> Dict:
        """
        Extract graph topology from Gx matrix.
        
        Args:
            Gx: Causal circuit matrix [N, N]
            threshold: Edge weight threshold
            top_k_nodes: If set, only keep top-k nodes by degree
        
        Returns:
            Dictionary with nodes, edges, and topology metrics
        """
        N = Gx.shape[0]
        
        # Build NetworkX graph
        G = nx.DiGraph()
        
        # Add all nodes
        for i in range(N):
            G.add_node(i)
        
        # Add edges above threshold
        edges = []
        edge_weights = []
        for i in range(N):
            for j in range(N):
                weight = Gx[i, j]
                if abs(weight) > threshold:
                    G.add_edge(i, j, weight=float(weight))
                    edges.append({
                        'source': int(i),
                        'target': int(j),
                        'weight': float(weight)
                    })
                    edge_weights.append(abs(weight))
        
        # Compute degree distribution
        in_degrees = dict(G.in_degree())
        out_degrees = dict(G.out_degree())
        total_degrees = {i: in_degrees[i] + out_degrees[i] for i in range(N)}
        
        degree_list = list(total_degrees.values())
        
        # Identify hub neurons (top 10% by degree)
        if len(degree_list) > 0:
            hub_threshold = np.percentile(degree_list, 90)
            hubs = [i for i, deg in total_degrees.items() if deg >= hub_threshold]
        else:
            hub_threshold = 0
            hubs = []
        
        # If top_k_nodes specified, filter to top-k by degree
        if top_k_nodes is not None and top_k_nodes < N:
            # Get top-k nodes by total degree
            top_nodes = sorted(total_degrees.items(), key=lambda x: x[1], reverse=True)[:top_k_nodes]
            top_node_ids = set([node_id for node_id, _ in top_nodes])
            
            # Filter edges to only include top nodes
            filtered_edges = [
                e for e in edges 
                if e['source'] in top_node_ids and e['target'] in top_node_ids
            ]
            edges = filtered_edges
            
            # Update nodes list
            nodes = [
                {
                    'id': int(node_id),
                    'degree': int(total_degrees[node_id]),
                    'in_degree': int(in_degrees[node_id]),
                    'out_degree': int(out_degrees[node_id]),
                    'is_hub': node_id in hubs
                }
                for node_id in top_node_ids
            ]
        else:
            nodes = [
                {
                    'id': int(i),
                    'degree': int(total_degrees[i]),
                    'in_degree': int(in_degrees[i]),
                    'out_degree': int(out_degrees[i]),
                    'is_hub': i in hubs
                }
                for i in range(N)
            ]
        
        # Compute modularity (if graph is not empty)
        try:
            if G.number_of_edges() > 0:
                # Convert to undirected for community detection
                G_undirected = G.to_undirected()
                communities = list(nx.community.greedy_modularity_communities(G_undirected))
                modularity = nx.community.modularity(G_undirected, communities)
            else:
                modularity = 0.0
                communities = []
        except:
            modularity = 0.0
            communities = []
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metrics': {
                'num_nodes': len(nodes),
                'num_edges': len(edges),
                'avg_degree': float(np.mean(degree_list)) if degree_list else 0.0,
                'max_degree': int(np.max(degree_list)) if degree_list else 0,
                'min_degree': int(np.min(degree_list)) if degree_list else 0,
                'std_degree': float(np.std(degree_list)) if degree_list else 0.0,
                'modularity': float(modularity),
                'num_communities': len(communities),
                'hub_threshold': float(hub_threshold),
                'num_hubs': len(hubs),
                'hubs': hubs,
                'degree_distribution': degree_list,
            }
        }
    
    @staticmethod
    def extract_activation_sparsity(
        y_activations: List[np.ndarray],
        x_activations: Optional[List[np.ndarray]] = None
    ) -> Dict:
        """
        Compute activation sparsity metrics.
        
        Args:
            y_activations: List of y activation matrices [L, T, N]
            x_activations: Optional list of x activation matrices [L, T, N]
        
        Returns:
            Sparsity metrics and heatmap data
        """
        # Stack activations [L, T, N]
        y_stack = np.stack(y_activations, axis=0)
        L, T, N = y_stack.shape
        
        # Compute sparsity per layer
        y_sparsity_per_layer = []
        for layer_idx in range(L):
            non_zero = (y_stack[layer_idx] != 0).mean()
            y_sparsity_per_layer.append(float(non_zero))
        
        # Compute sparsity per token (averaged across layers)
        y_sparsity_per_token = []
        for token_idx in range(T):
            non_zero = (y_stack[:, token_idx, :] != 0).mean()
            y_sparsity_per_token.append(float(non_zero))
        
        # Average activation per neuron (across layers and tokens)
        y_avg_activation = y_stack.mean(axis=(0, 1))  # [N]
        
        # Activation frequency per neuron
        y_activation_frequency = (y_stack != 0).mean(axis=(0, 1))  # [N]
        
        result = {
            'y_sparsity_per_layer': y_sparsity_per_layer,
            'y_sparsity_per_token': y_sparsity_per_token,
            'y_avg_sparsity': float(np.mean(y_sparsity_per_layer)),
            'y_std_sparsity': float(np.std(y_sparsity_per_layer)),
            'y_heatmap': y_stack.tolist(),  # [L, T, N] for visualization
            'y_neuron_metrics': {
                'avg_activation': y_avg_activation.tolist(),
                'activation_frequency': y_activation_frequency.tolist(),
            }
        }
        
        # If x_activations provided, compute x sparsity too
        if x_activations is not None:
            x_stack = np.stack(x_activations, axis=0)
            
            x_sparsity_per_layer = []
            for layer_idx in range(L):
                non_zero = (x_stack[layer_idx] != 0).mean()
                x_sparsity_per_layer.append(float(non_zero))
            
            result['x_sparsity_per_layer'] = x_sparsity_per_layer
            result['x_avg_sparsity'] = float(np.mean(x_sparsity_per_layer))
            result['x_std_sparsity'] = float(np.std(x_sparsity_per_layer))
        
        return result
    
    @staticmethod
    def extract_attention_flow(
        attention_weights: List[np.ndarray],
        top_k: int = 30
    ) -> Dict:
        """
        Extract attention flow patterns.
        
        Args:
            attention_weights: List of attention matrices [L, B, T, T]
            top_k: Number of top attention edges to keep per layer
        
        Returns:
            Attention flow data
        """
        # Stack and average over batch: [L, T, T]
        attn_stack = np.stack([a.mean(axis=0) for a in attention_weights], axis=0)
        L, T, _ = attn_stack.shape
        
        # Extract top-k attention edges per layer
        attention_edges_per_layer = []
        for layer_idx in range(L):
            attn_matrix = attn_stack[layer_idx]  # [T, T]
            
            # Get top-k edges
            flat_indices = np.argsort(attn_matrix.flatten())[-top_k:]
            edges = []
            for flat_idx in flat_indices:
                source = int(flat_idx // T)
                target = int(flat_idx % T)
                weight = float(attn_matrix[source, target])
                edges.append({
                    'source': source,
                    'target': target,
                    'weight': weight
                })
            
            attention_edges_per_layer.append(edges)
        
        # Average attention per layer
        avg_attention_per_layer = attn_stack.mean(axis=(1, 2)).tolist()
        
        return {
            'attention_per_layer': [a.tolist() for a in attn_stack],
            'attention_edges_per_layer': attention_edges_per_layer,
            'avg_attention_per_layer': avg_attention_per_layer,
        }
    
    @staticmethod
    def identify_concept_neurons(
        y_activations: List[np.ndarray],
        input_tokens: np.ndarray,
        vocab_size: int,
        threshold: float = 0.5
    ) -> Dict:
        """
        Identify neurons that consistently activate for specific tokens (concepts).
        
        Args:
            y_activations: List of y activation matrices [L, T, N]
            input_tokens: Input token IDs [T]
            vocab_size: Size of vocabulary
            threshold: Activation threshold
        
        Returns:
            Concept-neuron mapping
        """
        # Stack activations [L, T, N]
        y_stack = np.stack(y_activations, axis=0)
        L, T, N = y_stack.shape
        
        # For each token type, find neurons that activate
        concept_neurons = defaultdict(list)
        
        for token_id in range(vocab_size):
            # Find positions where this token appears
            token_positions = np.where(input_tokens == token_id)[0]
            
            if len(token_positions) == 0:
                continue
            
            # Get activations at these positions (averaged across layers)
            token_activations = y_stack[:, token_positions, :].mean(axis=(0, 1))  # [N]
            
            # Find neurons with high activation
            active_neurons = np.where(token_activations > threshold)[0]
            
            concept_neurons[int(token_id)] = [
                {
                    'neuron_id': int(neuron_id),
                    'avg_activation': float(token_activations[neuron_id])
                }
                for neuron_id in active_neurons
            ]
        
        return dict(concept_neurons)
    
    @staticmethod
    def compute_layer_statistics(
        y_activations: List[np.ndarray],
        x_activations: List[np.ndarray]
    ) -> Dict:
        """
        Compute per-layer statistics.
        
        Args:
            y_activations: List of y activation matrices [L, T, N]
            x_activations: List of x activation matrices [L, T, N]
        
        Returns:
            Layer statistics
        """
        L = len(y_activations)
        
        stats = []
        for layer_idx in range(L):
            y = y_activations[layer_idx]
            x = x_activations[layer_idx]
            
            layer_stats = {
                'layer': layer_idx,
                'y_mean': float(y.mean()),
                'y_std': float(y.std()),
                'y_max': float(y.max()),
                'y_min': float(y.min()),
                'y_sparsity': float((y != 0).mean()),
                'x_mean': float(x.mean()),
                'x_std': float(x.std()),
                'x_max': float(x.max()),
                'x_min': float(x.min()),
                'x_sparsity': float((x != 0).mean()),
            }
            stats.append(layer_stats)
        
        return {'layer_statistics': stats}


if __name__ == '__main__':
    """Test state extraction"""
    print("Testing State Extraction Utilities...")
    
    # Test graph topology extraction
    print("\n1. Testing graph topology extraction...")
    N = 100
    Gx = np.random.randn(N, N) * 0.1
    # Add some strong connections to create hubs
    Gx[0, :] = np.random.randn(N) * 0.5  # Node 0 is a hub
    Gx[:, 0] = np.random.randn(N) * 0.5
    
    topology = StateExtractor.extract_graph_topology(Gx, threshold=0.1, top_k_nodes=20)
    print(f"   Nodes: {len(topology['nodes'])}")
    print(f"   Edges: {len(topology['edges'])}")
    print(f"   Avg degree: {topology['metrics']['avg_degree']:.2f}")
    print(f"   Num hubs: {topology['metrics']['num_hubs']}")
    
    # Test sparsity extraction
    print("\n2. Testing sparsity extraction...")
    L, T, N = 12, 100, 2048
    y_activations = [np.random.rand(T, N) * (np.random.rand(T, N) > 0.95) for _ in range(L)]
    
    sparsity = StateExtractor.extract_activation_sparsity(y_activations)
    print(f"   Avg sparsity: {sparsity['y_avg_sparsity']:.4f}")
    print(f"   Std sparsity: {sparsity['y_std_sparsity']:.4f}")
    print(f"   Sparsity per layer: {len(sparsity['y_sparsity_per_layer'])} values")
    
    # Test attention flow extraction
    print("\n3. Testing attention flow extraction...")
    attention_weights = [np.random.rand(1, T, T) for _ in range(L)]
    
    attention_flow = StateExtractor.extract_attention_flow(attention_weights, top_k=10)
    print(f"   Attention layers: {len(attention_flow['attention_per_layer'])}")
    print(f"   Top edges per layer: {len(attention_flow['attention_edges_per_layer'][0])}")
    
    # Test concept neuron identification
    print("\n4. Testing concept neuron identification...")
    input_tokens = np.random.randint(0, 5, T)
    
    concept_neurons = StateExtractor.identify_concept_neurons(
        y_activations, input_tokens, vocab_size=5, threshold=0.1
    )
    print(f"   Concepts found: {len(concept_neurons)}")
    for token_id, neurons in concept_neurons.items():
        print(f"   Token {token_id}: {len(neurons)} neurons")
    
    print("\n✅ All tests passed!")
