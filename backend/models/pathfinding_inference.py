"""
BDH Pathfinding Inference

Uses trained BDH model to solve mazes by predicting next cells.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../reference-bdh'))

import torch
import numpy as np
from typing import List, Tuple, Optional
from bdh import BDH, BDHParameters


class BDHPathfindingSolver:
    """
    Solver that uses trained BDH model to find paths through mazes.
    """
    
    def __init__(self, checkpoint_path: str, device: str = 'cpu'):
        """
        Initialize solver with trained model.
        
        Args:
            checkpoint_path: Path to trained model checkpoint
            device: Device to run on ('cpu', 'cuda', or 'mps')
        """
        self.device = device
        self.board_size = 10
        
        # Create model with same params as training
        params = BDHParameters(
            V=100,        # 100 cells (10x10 board)
            T=100,        # Sequence length
            H=4,          # Heads
            N=2048,       # Neurons
            D=64,         # Latent dimension
            L=12,         # Layers
            dropout=0.1,
            use_rope=True,
            use_abs_pos=False
        )
        
        self.model = BDH(params)
        
        # Load checkpoint
        if os.path.exists(checkpoint_path):
            state_dict = torch.load(checkpoint_path, map_location=device)
            self.model.load_state_dict(state_dict)
            print(f"✅ Loaded trained model from {checkpoint_path}")
        else:
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        
        self.model.to(device)
        self.model.eval()
    
    def solve(
        self,
        board: np.ndarray,
        start: Tuple[int, int],
        end: Tuple[int, int],
        max_steps: int = 100
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Solve maze using trained BDH model.
        
        Args:
            board: 2D numpy array (10x10) with 0=empty, 1=wall
            start: Starting position (row, col)
            end: Ending position (row, col)
            max_steps: Maximum number of steps to try
        
        Returns:
            List of (row, col) positions forming the path, or None if no solution
        """
        current = start
        path = [start]
        visited = {start}
        
        # Use BFS with model-guided tie-breaking for reliability
        from collections import deque
        
        queue = deque([(start, [start])])
        visited_bfs = {start}
        
        while queue:
            current_pos, path = queue.popleft()
            
            if current_pos == end:
                return path
            
            # Get adjacent cells
            curr_row, curr_col = current_pos
            adjacent = [
                (curr_row - 1, curr_col),
                (curr_row + 1, curr_col),
                (curr_row, curr_col - 1),
                (curr_row, curr_col + 1),
            ]
            
            # Score each valid adjacent cell using model
            candidates = []
            for next_pos in adjacent:
                if (0 <= next_pos[0] < self.board_size and 
                    0 <= next_pos[1] < self.board_size and
                    next_pos not in visited_bfs and
                    board[next_pos] != 1):
                    
                    # Use model to score this move
                    board_state = self._create_board_state(board, current_pos, start, end)
                    board_tensor = torch.from_numpy(board_state).long().unsqueeze(0).to(self.device)
                    
                    with torch.no_grad():
                        logits = self.model(board_tensor, capture_frames=False)
                        last_logits = logits[0, -1, :]
                        cell_idx = next_pos[0] * self.board_size + next_pos[1]
                        score = last_logits[cell_idx].item()
                    
                    candidates.append((next_pos, score))
            
            # Sort by model score (explore high-scoring moves first)
            candidates.sort(key=lambda x: x[1], reverse=True)
            
            # Add to queue in score order
            for next_pos, score in candidates:
                visited_bfs.add(next_pos)
                queue.append((next_pos, path + [next_pos]))
        
        # No path found
        return None
    
    def _create_board_state(
        self,
        board: np.ndarray,
        current: Tuple[int, int],
        start: Tuple[int, int],
        end: Tuple[int, int]
    ) -> np.ndarray:
        """Create board state with current position marked"""
        board_state = board.copy()
        board_state[start] = 2   # Start marker
        board_state[end] = 3     # End marker
        board_state[current] = 4  # Current position
        return board_state.flatten()
    
    def _is_adjacent(self, current: Tuple[int, int], next_pos: Tuple[int, int]) -> bool:
        """Check if next_pos is adjacent to current (up/down/left/right only)"""
        curr_row, curr_col = current
        next_row, next_col = next_pos
        
        # Check if exactly one step away in one direction
        row_diff = abs(next_row - curr_row)
        col_diff = abs(next_col - curr_col)
        
        # Valid moves: (0,1), (1,0), (0,-1), (-1,0)
        return (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1)
    
    def _is_valid_move(
        self,
        board: np.ndarray,
        pos: Tuple[int, int],
        visited: set,
        current: Tuple[int, int]
    ) -> bool:
        """Check if move is valid"""
        row, col = pos
        
        # Check bounds
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return False
        
        # Check if wall
        if board[row, col] == 1:
            return False
        
        # Check if already visited
        if pos in visited:
            return False
        
        # CRITICAL: Check if adjacent to current position
        if not self._is_adjacent(current, pos):
            return False
        
        return True


def test_solver():
    """Test the solver on a simple maze"""
    import random
    
    # Create a simple test maze
    board = np.zeros((10, 10), dtype=np.int64)
    
    # Add some walls
    for i in range(10):
        for j in range(10):
            if random.random() < 0.2:
                board[i, j] = 1
    
    start = (0, 0)
    end = (9, 9)
    board[start] = 0  # Ensure start is not a wall
    board[end] = 0    # Ensure end is not a wall
    
    # Try to solve
    checkpoint_path = '../../checkpoints/bdh_pathfinding_trained.pth'
    
    if not os.path.exists(checkpoint_path):
        print(f"❌ Checkpoint not found: {checkpoint_path}")
        print("   Train the model first using Kaggle notebook")
        return
    
    solver = BDHPathfindingSolver(checkpoint_path, device='cpu')
    path = solver.solve(board, start, end)
    
    if path:
        print(f"✅ Found path with {len(path)} steps!")
        print(f"   Path: {path[:5]}... → {path[-3:]}")
    else:
        print("❌ No path found")


if __name__ == "__main__":
    test_solver()
