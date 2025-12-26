"""
Pathfinding Dataset Generator for BDH Training

Generates maze boards with BFS solutions for training BDH to learn pathfinding.
"""

import numpy as np
import torch
from collections import deque
from typing import List, Tuple, Optional
import random


class PathfindingDataset(torch.utils.data.Dataset):
    """
    Dataset for training BDH on pathfinding tasks.
    
    Each sample consists of:
    - Input: Flattened board state (0=empty, 1=wall, 2=start, 3=end, 4=current_pos)
    - Target: Next cell index in optimal path
    """
    
    def __init__(
        self,
        num_samples: int = 50000,
        board_size: int = 10,
        wall_density: float = 0.25,
        min_path_length: int = 5
    ):
        self.num_samples = num_samples
        self.board_size = board_size
        self.wall_density = wall_density
        self.min_path_length = min_path_length
        self.vocab_size = 5  # 0=empty, 1=wall, 2=start, 3=end, 4=path
        
        print(f"Generating {num_samples} pathfinding samples...")
        self.samples = self._generate_dataset()
        print(f"✓ Generated {len(self.samples)} valid samples")
    
    def _generate_board(self) -> np.ndarray:
        """Generate a random board with walls"""
        board = np.zeros((self.board_size, self.board_size), dtype=np.int64)
        
        # Add random walls
        for i in range(self.board_size):
            for j in range(self.board_size):
                if random.random() < self.wall_density:
                    board[i, j] = 1
        
        return board
    
    def _bfs_path(
        self,
        board: np.ndarray,
        start: Tuple[int, int],
        end: Tuple[int, int]
    ) -> Optional[List[Tuple[int, int]]]:
        """Find shortest path using BFS"""
        queue = deque([(start, [start])])
        visited = {start}
        
        while queue:
            (row, col), path = queue.popleft()
            
            if (row, col) == end:
                return path
            
            # Check 4 directions
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_row, new_col = row + dr, col + dc
                
                if (0 <= new_row < self.board_size and
                    0 <= new_col < self.board_size and
                    (new_row, new_col) not in visited and
                    board[new_row, new_col] != 1):
                    
                    visited.add((new_row, new_col))
                    queue.append(((new_row, new_col), path + [(new_row, new_col)]))
        
        return None
    
    def _generate_sample(self) -> Optional[Tuple[np.ndarray, int]]:
        """Generate a single training sample"""
        max_attempts = 10
        
        for _ in range(max_attempts):
            # Generate board
            board = self._generate_board()
            
            # Random start and end positions
            start = (random.randint(0, self.board_size - 1),
                    random.randint(0, self.board_size - 1))
            end = (random.randint(0, self.board_size - 1),
                  random.randint(0, self.board_size - 1))
            
            # Ensure start and end are not walls and not the same
            if (board[start] == 1 or board[end] == 1 or start == end):
                continue
            
            # Find path
            path = self._bfs_path(board, start, end)
            
            if path is None or len(path) < self.min_path_length:
                continue
            
            # Create training samples from path
            # For each position in path (except last), predict next position
            samples = []
            for i in range(len(path) - 1):
                # Create board state with current position marked
                board_state = board.copy()
                board_state[start] = 2  # Start
                board_state[end] = 3    # End
                board_state[path[i]] = 4  # Current position
                
                # Target is next position in path
                next_pos = path[i + 1]
                target_idx = next_pos[0] * self.board_size + next_pos[1]
                
                samples.append((board_state.flatten(), target_idx))
            
            return samples
        
        return None
    
    def _generate_dataset(self) -> List[Tuple[np.ndarray, int]]:
        """Generate full dataset"""
        samples = []
        attempts = 0
        max_attempts = self.num_samples * 3
        
        while len(samples) < self.num_samples and attempts < max_attempts:
            sample_set = self._generate_sample()
            if sample_set:
                samples.extend(sample_set)
            attempts += 1
            
            if attempts % 1000 == 0:
                print(f"  Generated {len(samples)}/{self.num_samples} samples...")
        
        # Trim to exact size
        return samples[:self.num_samples]
    
    def __len__(self) -> int:
        return len(self.samples)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        board_state, target = self.samples[idx]
        return (
            torch.from_numpy(board_state).long(),
            torch.tensor(target, dtype=torch.long)
        )


if __name__ == "__main__":
    # Test dataset generation
    dataset = PathfindingDataset(num_samples=1000, board_size=10)
    print(f"\nDataset created with {len(dataset)} samples")
    
    # Test a sample
    board, target = dataset[0]
    print(f"Board shape: {board.shape}")
    print(f"Target: {target}")
    print(f"Board values: {torch.unique(board)}")
