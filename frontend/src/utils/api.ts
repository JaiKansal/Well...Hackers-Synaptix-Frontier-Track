/**
 * API Client for BDH Brain Explorer
 * 
 * Handles all communication with the FastAPI backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface InferenceRequest {
  input_tokens: number[];
  track_states: boolean;
}

export interface SparsityMetrics {
  y_sparsity_mean: number;
  y_sparsity_std: number;
  y_sparsity_min: number;
  y_sparsity_max: number;
  y_sparsity_per_layer: number[];
  x_sparsity_mean: number;
  x_sparsity_std: number;
  x_sparsity_per_layer: number[];
}

export interface InferenceResponse {
  predictions: number[];
  states?: {
    y_activations: number[][][];  // [layers, tokens, neurons]
    x_activations: number[][][];
    attention_weights: number[][][][];
    output_frames: number[][];
    logits_frames: number[][][];
    sparsity_per_layer: number[];
    Gx_topology: number[][];
    Gy_topology: number[][];
  };
  sparsity?: SparsityMetrics;
}

export interface TopologyNode {
  id: number;
  degree: number;
  in_degree: number;
  out_degree: number;
  is_hub: boolean;
}

export interface TopologyEdge {
  source: number;
  target: number;
  weight: number;
}

export interface TopologyMetrics {
  num_neurons: number;
  num_edges: number;
  avg_degree: number;
  max_degree: number;
  min_degree: number;
  std_degree: number;
  hub_threshold: number;
  num_hubs: number;
  hub_indices: number[];
}

export interface TopologyResponse {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  metrics: TopologyMetrics;
}

// API Functions

/**
 * Get API health status
 */
export const getHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

/**
 * Get model configuration
 */
export const getConfig = async () => {
  const response = await apiClient.get('/api/config');
  return response.data;
};

/**
 * Run BDH inference
 */
export const runInference = async (
  request: InferenceRequest
): Promise<InferenceResponse> => {
  const response = await apiClient.post<InferenceResponse>('/api/infer', request);
  return response.data;
};

/**
 * Get graph topology
 */
export const getTopology = async (
  threshold: number = 0.1,
  topKNodes?: number
): Promise<TopologyResponse> => {
  const params: any = { threshold };
  if (topKNodes) params.top_k_nodes = topKNodes;
  
  const response = await apiClient.get<TopologyResponse>('/api/topology', { params });
  return response.data;
};

/**
 * Measure sparsity
 */
export const measureSparsity = async (
  request: InferenceRequest
): Promise<SparsityMetrics> => {
  const response = await apiClient.post<SparsityMetrics>('/api/sparsity', request);
  return response.data;
};

/**
 * Solve pathfinding task
 */
export const solvePathfinding = async (board: number[][]) => {
  const response = await apiClient.post('/api/pathfind', { board });
  return response.data;
};

export default apiClient;
