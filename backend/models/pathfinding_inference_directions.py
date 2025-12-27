"""
BDH Pathfinding Inference (Direction-Based)

Uses trained BDH model that predicts DIRECTIONS (0-3) instead of cells.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../reference-bdh'))

import torch
import numpy as np
from typing import List, Tuple, Optional
from bdh import BDH, BDHParameters


class BDHPathfindingSolverDirections:
    """
    Solver using direction-based BDH model (V=4)
    """
    
    # Direction mappings
    DIRECTIONS = {
        0: (-1, 0),  # Up
        1: (1, 0),   # Down
        2: (0, -1),  # Left
        3: (0, 1),   # Right
    }
    
    def __init__(self, checkpoint_path: str, device: str = 'cpu'):
        self.device = device
        self.board_size = 10
        
        # Model with V=4 (4 directions)
        params = BDHParameters(
            V=4,          # 4 directions!
            T=100,
            H=4,
            N=2048,
            D=64,
            L=12,
            dropout=0.1,
            use_rope=True,
            use_abs_pos=False
        )
        
        self.model = BDH(params)
        
        if os.path.exists(checkpoint_path):
            state_dict = torch.load(checkpoint_path, map_location=device)
            self.model.load_state_dict(state_dict)
            print(f\"✅ Loaded direction-based model from {checkpoint_path}\")\n        else:
            raise FileNotFoundError(f\"Checkpoint not found: {checkpoint_path}\")\n        
        self.model.to(device)
        self.model.eval()
    
    def solve(
        self,
        board: np.ndarray,
        start: Tuple[int, int],
        end: Tuple[int, int],
        max_steps: int = 100
    ) -> Optional[List[Tuple[int, int]]]:
        \"\"\"Solve maze using direction predictions\"\"\"
        current = start
        path = [start]
        visited = {start}
        
        with torch.no_grad():
            for step in range(max_steps):
                if current == end:
                    return path
                
                # Create board state
                board_state = self._create_board_state(board, current, start, end)
                board_tensor = torch.from_numpy(board_state).long().unsqueeze(0).to(self.device)
                
                # Predict direction
                logits = self.model(board_tensor, capture_frames=False)
                last_logits = logits[0, -1, :]  # [4] - one score per direction
                
                # Try directions in order of model preference
                direction_scores = [(i, last_logits[i].item()) for i in range(4)]
                direction_scores.sort(key=lambda x: x[1], reverse=True)
                
                next_cell = None
                for direction_idx, score in direction_scores:
                    dr, dc = self.DIRECTIONS[direction_idx]
                    candidate = (current[0] + dr, current[1] + dc)
                    
                    if self._is_valid_move(board, candidate, visited):
                        next_cell = candidate
                        break
                
                if next_cell is None:
                    # No valid moves
                    return None
                
                path.append(next_cell)
                visited.add(next_cell)
                current = next_cell
        
        return None if current != end else path
    
    def _create_board_state(self, board, current, start, end):
        board_state = board.copy()
        board_state[start] = 2
        board_state[end] = 3
        board_state[current] = 4
        return board_state.flatten()
    
    def _is_valid_move(self, board, pos, visited):
        row, col = pos
        if not (0 <= row < self.board_size and 0 <= col < self.board_size):
            return False
        if board[row, col] == 1:
            return False
        if pos in visited:
            return False
        return True
