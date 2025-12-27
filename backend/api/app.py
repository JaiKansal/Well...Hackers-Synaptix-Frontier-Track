"""
FastAPI Backend for BDH Brain Explorer

This API provides endpoints for:
- BDH inference with state tracking
- Graph topology extraction
- Sparsity measurements
- Pathfinding visualization
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../reference-bdh'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../models'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import torch
import numpy as np
import json

from bdh_instrumented import BDHInstrumented, load_instrumented_bdh
from state_extractor import StateExtractor
from bdh import BDHParameters

# Initialize FastAPI app
app = FastAPI(
    title="BDH Brain Explorer API",
    description="API for visualizing Baby Dragon Hatchling (BDH) architecture",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model cache
MODEL_CACHE = {
    'model': None,
    'config': None,
    'device': None
}


# ============================================================================
# Pydantic Models (Request/Response Schemas)
# ============================================================================

class InferenceRequest(BaseModel):
    """Request for BDH inference"""
    input_tokens: List[int] = Field(..., description="List of token IDs")
    track_states: bool = Field(default=True, description="Whether to track internal states")
    
    class Config:
        json_schema_extra = {
            "example": {
                "input_tokens": [0, 1, 2, 3, 4],
                "track_states": True
            }
        }


class SparsityMetrics(BaseModel):
    """Sparsity measurement results"""
    y_sparsity_mean: float
    y_sparsity_std: float
    y_sparsity_min: float
    y_sparsity_max: float
    y_sparsity_per_layer: List[float]
    x_sparsity_mean: float
    x_sparsity_std: float
    x_sparsity_per_layer: List[float]


class TopologyMetrics(BaseModel):
    """Graph topology metrics"""
    num_neurons: int
    num_edges: int
    avg_degree: float
    max_degree: int
    min_degree: int
    std_degree: float
    hub_threshold: float
    num_hubs: int
    hub_indices: List[int]


class InferenceResponse(BaseModel):
    """Response from BDH inference"""
    predictions: List[int]
    states: Optional[Dict[str, Any]] = None
    sparsity: Optional[SparsityMetrics] = None


class TopologyResponse(BaseModel):
    """Response with graph topology"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    metrics: TopologyMetrics


class PathfindingRequest(BaseModel):
    """Request for pathfinding task"""
    board: List[List[int]] = Field(..., description="2D board grid")
    
    class Config:
        json_schema_extra = {
            "example": {
                "board": [
                    [0, 0, 1, 0],
                    [2, 0, 1, 0],
                    [0, 0, 0, 3],
                    [0, 1, 0, 0]
                ]
            }
        }


# ============================================================================
# Helper Functions
# ============================================================================

def get_device():
    """Get available device (CUDA > MPS > CPU)"""
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    else:
        return torch.device("cpu")


def load_model():
    """Load BDH model (trained checkpoint if available, random otherwise)"""
    if MODEL_CACHE['model'] is None:
        from pathlib import Path
        
        # Check for trained checkpoint
        checkpoint_path = Path(__file__).parent / '../../checkpoints/bdh_trained.pth'
        
        # Create model parameters
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
        
        device = get_device()
        model = BDHInstrumented(params)
        
        # Try to load trained checkpoint
        if checkpoint_path.exists():
            print("=" * 60)
            print("🎓 TRAINED MODEL MODE")
            print("=" * 60)
            print(f"✓ Loading trained checkpoint from: {checkpoint_path}")
            try:
                state_dict = torch.load(checkpoint_path, map_location=device)
                model.load_state_dict(state_dict)
                MODEL_CACHE['is_trained'] = True
                MODEL_CACHE['checkpoint_path'] = str(checkpoint_path)
                print("✓ Trained model loaded successfully!")
                print("✓ Expected sparsity: ~5% (learned sparse representations)")
                print("=" * 60)
            except Exception as e:
                print(f"⚠ Error loading checkpoint: {e}")
                print("⚠ Falling back to random initialization")
                MODEL_CACHE['is_trained'] = False
                MODEL_CACHE['checkpoint_path'] = None
        else:
            print("=" * 60)
            print("🎲 DEMO MODE (Random Initialization)")
            print("=" * 60)
            print("⚠ No trained checkpoint found")
            print(f"  Looked in: {checkpoint_path}")
            print("✓ Using random initialization for demonstration")
            print("✓ Expected sparsity: ~25% (natural ReLU sparsity)")
            print("")
            print("💡 To use trained model:")
            print("   1. Train on Kaggle (see TRAINING.md)")
            print("   2. Place checkpoint at: checkpoints/bdh_trained.pth")
            print("   3. Restart backend")
            print("=" * 60)
            MODEL_CACHE['is_trained'] = False
            MODEL_CACHE['checkpoint_path'] = None
        
        model.to(device)
        model.eval()
        
        MODEL_CACHE['model'] = model
        MODEL_CACHE['device'] = device
        MODEL_CACHE['config'] = params
        
        print(f"✓ Model ready on {device}")
    
    return MODEL_CACHE['model'], MODEL_CACHE['device'], MODEL_CACHE['config']


def convert_numpy_to_python(obj):
    """Recursively convert numpy types to Python types for JSON serialization"""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_numpy_to_python(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_python(item) for item in obj]
    else:
        return obj


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "BDH Brain Explorer API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "inference": "/api/infer",
            "topology": "/api/topology",
            "sparsity": "/api/sparsity",
            "pathfind": "/api/pathfind",
            "model_status": "/api/model-status",
            "health": "/health"
        }
    }


@app.get("/api/model-status")
async def get_model_status():
    """Get model training status"""
    load_model()  # Ensure model is checked
    
    is_trained = MODEL_CACHE.get('is_trained', False)
    checkpoint_path = MODEL_CACHE.get('checkpoint_path')
    
    return {
        "is_trained": is_trained,
        "device": str(MODEL_CACHE.get('device', 'cpu')),
        "checkpoint_available": checkpoint_path is not None,
        "checkpoint_path": checkpoint_path,
        "expected_sparsity": "5%" if is_trained else "~25%",
        "note": "Trained model demonstrates learned sparsity" if is_trained 
                else "Random model for demonstration (train on GPU for 5% sparsity)"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model, device, config = load_model()
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(device),
        "config": {
            "neurons": config.N,
            "layers": config.L,
            "heads": config.H
        }
    }


@app.post("/api/infer")
async def infer(request: InferenceRequest):
    """
    Run BDH inference on input tokens
    
    Returns predictions and optionally internal states
    """
    try:
        model, device, _ = load_model()
        
        # Convert input to tensor
        input_tokens = torch.tensor([request.input_tokens], dtype=torch.long).to(device)
        
        # Run inference
        with torch.no_grad():
            if request.track_states:
                model.enable_tracking()
                logits, output_frames, x_frames, y_frames, attn_frames, logits_frames = \
                    model(input_tokens, capture_frames=True)
                
                states = model.get_states()
                
                # Convert states to JSON-serializable format
                states_json = convert_numpy_to_python(states)
                
                # Measure sparsity
                sparsity_metrics = model.measure_sparsity(input_tokens)
                
                response = InferenceResponse(
                    predictions=logits.argmax(dim=-1).squeeze(0).cpu().tolist(),
                    states=states_json,
                    sparsity=SparsityMetrics(**sparsity_metrics)
                )
            else:
                logits = model(input_tokens, capture_frames=False)
                response = InferenceResponse(
                    predictions=logits.argmax(dim=-1).squeeze(0).cpu().tolist()
                )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/topology")
async def get_topology(
    threshold: float = 0.1,
    top_k_nodes: Optional[int] = None
):
    """
    Get BDH graph topology (Gx matrix)
    
    Args:
        threshold: Edge weight threshold for filtering
        top_k_nodes: If set, return only top-k nodes by degree
    
    Returns:
        Graph topology with nodes, edges, and metrics
    """
    try:
        model, device, _ = load_model()
        
        # Extract Gx topology
        Gx, Gy = model.extract_graph_topologies()
        
        # Use StateExtractor for detailed analysis
        topology = StateExtractor.extract_graph_topology(
            Gx,
            threshold=threshold,
            top_k_nodes=top_k_nodes
        )
        
        # Convert to response format
        response = TopologyResponse(
            nodes=topology['nodes'],
            edges=topology['edges'],
            metrics=TopologyMetrics(**topology['metrics'])
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sparsity")
async def measure_sparsity(request: InferenceRequest):
    """
    Measure activation sparsity on given input
    
    Returns detailed sparsity metrics
    """
    try:
        model, device, _ = load_model()
        
        # Convert input to tensor
        input_tokens = torch.tensor([request.input_tokens], dtype=torch.long).to(device)
        
        # Measure sparsity
        sparsity_metrics = model.measure_sparsity(input_tokens)
        
        return SparsityMetrics(**sparsity_metrics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pathfind")
async def pathfind(request: PathfindingRequest):
    """
    Solve pathfinding task with BDH
    
    Takes a 2D board and returns the solution with visualization data
    """
    try:
        model, device, _ = load_model()
        
        # Flatten board to token sequence
        board = np.array(request.board)
        board_flat = board.flatten()
        input_tokens = torch.tensor([board_flat], dtype=torch.long).to(device)
        
        # Run inference with state tracking
        model.enable_tracking()
        with torch.no_grad():
            logits, output_frames, x_frames, y_frames, attn_frames, logits_frames = \
                model(input_tokens, capture_frames=True)
        
        states = model.get_states()
        predictions = logits.argmax(dim=-1).squeeze(0).cpu().numpy()
        
        # Reshape predictions back to 2D
        board_size = board.shape[0]
        predicted_board = predictions.reshape(board_size, board_size)
        
        # Find start and end positions
        start_pos = None
        end_pos = None
        for i in range(board_size):
            for j in range(board_size):
                if board[i][j] == 2:
                    start_pos = (i, j)
                elif board[i][j] == 3:
                    end_pos = (i, j)
        
        # Simple BFS pathfinding
        solution = []
        if start_pos and end_pos:
            from collections import deque
            
            queue = deque([(start_pos, [start_pos])])
            visited = {start_pos}
            
            while queue:
                (row, col), path = queue.popleft()
                
                if (row, col) == end_pos:
                    solution = [[r, c] for r, c in path]
                    break
                
                # Check 4 directions
                for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    new_row, new_col = row + dr, col + dc
                    
                    if (0 <= new_row < board_size and 
                        0 <= new_col < board_size and
                        (new_row, new_col) not in visited and
                        board[new_row][new_col] != 1):  # Not a wall
                        
                        visited.add((new_row, new_col))
                        queue.append(((new_row, new_col), path + [(new_row, new_col)]))
        
        # Extract visualization data
        sparsity = StateExtractor.extract_activation_sparsity(
            states['y_activations'],
            states['x_activations']
        )
        
        attention_flow = StateExtractor.extract_attention_flow(
            states['attention_weights'],
            top_k=30
        )
        
        return {
            "solution": solution,  # Add solution path
            "input_board": board.tolist(),
            "predicted_board": predicted_board.tolist(),
            "predictions": predictions.tolist(),
            "sparsity": {
                "y_sparsity_mean": sparsity['y_avg_sparsity'],
                "y_per_layer": sparsity['y_sparsity_per_layer'],
                "x_avg": sparsity['x_avg_sparsity'],
            },
            "attention_flow": {
                "edges_per_layer": attention_flow['attention_edges_per_layer'],
                "avg_per_layer": attention_flow['avg_attention_per_layer'],
            },
            "states": convert_numpy_to_python(states)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pathfind-model")
async def pathfind_with_model(request: PathfindingRequest):
    """
    Solve pathfinding using trained BDH model
    
    Uses the trained pathfinding model if available, otherwise falls back to BFS.
    Returns both model solution and BFS solution for comparison.
    """
    try:
        # Get board and positions
        board = np.array(request.board)
        board_size = board.shape[0]
        
        # Find start and end positions
        start_pos = None
        end_pos = None
        for i in range(board_size):
            for j in range(board_size):
                if board[i][j] == 2:
                    start_pos = (i, j)
                elif board[i][j] == 3:
                    end_pos = (i, j)
        
        if not start_pos or not end_pos:
            raise HTTPException(status_code=400, detail="Board must have start (2) and end (3) positions")
        
        # BFS solution (always compute as fallback/comparison)
        from collections import deque
        
        queue = deque([(start_pos, [start_pos])])
        visited = {start_pos}
        bfs_solution = []
        
        while queue:
            (row, col), path = queue.popleft()
            
            if (row, col) == end_pos:
                bfs_solution = [[r, c] for r, c in path]
                break
            
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_row, new_col = row + dr, col + dc
                
                if (0 <= new_row < board_size and 
                    0 <= new_col < board_size and
                    (new_row, new_col) not in visited and
                    board[new_row][new_col] != 1):
                    
                    visited.add((new_row, new_col))
                    queue.append(((new_row, new_col), path + [(new_row, new_col)]))
        
        # Try model-based solution
        model_solution = None
        model_available = False
        model_error = None
        
        try:
            # Check if pathfinding model checkpoint exists
            checkpoint_path = Path(__file__).parent / '../../checkpoints/bdh_pathfinding_trained.pth'
            
            if checkpoint_path.exists():
                # Import solver
                import sys
                sys.path.append(str(Path(__file__).parent / '../models'))
                from pathfinding_inference import BDHPathfindingSolver
                
                # Create solver
                device = 'cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu')
                solver = BDHPathfindingSolver(str(checkpoint_path), device=device)
                
                # Solve
                path = solver.solve(board, start_pos, end_pos, max_steps=100)
                
                if path:
                    model_solution = [[r, c] for r, c in path]
                    model_available = True
                else:
                    model_error = "Model could not find a solution"
            else:
                model_error = "Trained model checkpoint not found"
                
        except Exception as e:
            model_error = f"Model inference failed: {str(e)}"
        
        # Get model and run visualization
        model, device, _ = load_model()
        board_flat = board.flatten()
        input_tokens = torch.tensor([board_flat], dtype=torch.long).to(device)
        
        model.enable_tracking()
        with torch.no_grad():
            logits, output_frames, x_frames, y_frames, attn_frames, logits_frames = \
                model(input_tokens, capture_frames=True)
        
        states = model.get_states()
        
        # Extract visualization data
        sparsity = StateExtractor.extract_activation_sparsity(
            states['y_activations'],
            states['x_activations']
        )
        
        attention_flow = StateExtractor.extract_attention_flow(
            states['attention_weights'],
            top_k=30
        )
        
        return {
            "model_available": model_available,
            "model_solution": model_solution,
            "model_error": model_error,
            "bfs_solution": bfs_solution,
            "solutions_match": model_solution == bfs_solution if model_solution else False,
            "model_steps": len(model_solution) if model_solution else None,
            "bfs_steps": len(bfs_solution),
            "input_board": board.tolist(),
            "sparsity": {
                "y_sparsity_mean": sparsity['y_avg_sparsity'],
                "y_per_layer": sparsity['y_sparsity_per_layer'],
                "x_avg": sparsity['x_avg_sparsity'],
            },
            "attention_flow": {
                "edges_per_layer": attention_flow['attention_edges_per_layer'],
                "avg_per_layer": attention_flow['avg_attention_per_layer'],
            },
            "states": convert_numpy_to_python(states)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/config")
async def get_config():
    """Get model configuration"""
    try:
        _, _, config = load_model()
        
        return {
            "vocabulary_size": config.V,
            "sequence_length": config.T,
            "num_heads": config.H,
            "num_neurons": config.N,
            "latent_dim": config.D,
            "num_layers": config.L,
            "dropout": config.dropout,
            "use_rope": config.use_rope,
            "use_abs_pos": config.use_abs_pos
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Starting BDH Brain Explorer API")
    print("="*60)
    
    # Pre-load model
    print("\n📦 Loading model...")
    load_model()
    
    print("\n✓ Model loaded successfully!")
    print("\n📡 Starting server on http://localhost:8000")
    print("📚 API docs available at http://localhost:8000/docs")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
