"""
Simple BDH Pathfinding Training

Clean approach: Set V=100 (num_cells) so BDH directly predicts next cell.
No projection head needed!
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../reference-bdh'))

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import time
import matplotlib.pyplot as plt
from pathfinding_dataset import PathfindingDataset
from bdh import BDH, BDHParameters


def train_bdh_pathfinding(
    num_samples: int = 10000,  # Start with smaller dataset for testing
    num_epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 3e-4,
    device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
    checkpoint_dir: str = '../../checkpoints'
):
    """
    Train BDH on pathfinding - SIMPLE VERSION
    
    Key insight: Set V=100 (number of cells) so BDH directly predicts next cell!
    """
    
    print("=" * 70)
    print("🎓 TRAINING BDH FOR PATHFINDING (Simple Approach)")
    print("=" * 70)
    print(f"Device: {device}")
    print(f"Samples: {num_samples}")
    print(f"Epochs: {num_epochs}")
    print(f"Batch size: {batch_size}")
    print("=" * 70)
    
    # Create dataset
    print("\n📦 Creating dataset...")
    dataset = PathfindingDataset(num_samples=num_samples, board_size=10)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    print(f"✓ Dataset: {len(dataset)} samples, {len(loader)} batches/epoch")
    
    # Create BDH model with V=100 (one class per cell)
    print("\n🧠 Creating BDH model...")
    params = BDHParameters(
        V=100,        # 100 cells (10x10 board) - THIS IS THE KEY!
        T=100,        # Sequence length (board size)
        H=4,          # Heads
        N=2048,       # Neurons
        D=64,         # Latent dimension
        L=12,         # Layers
        dropout=0.1,
        use_rope=True,
        use_abs_pos=False
    )
    
    model = BDH(params)
    model.to(device)
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"✓ Model created: {total_params:,} parameters")
    print(f"✓ Vocabulary size: {params.V} (maps to {10}x{10} board)")
    
    # Optimizer and loss
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
    criterion = nn.CrossEntropyLoss()
    
    # Training loop
    print("\n🚀 Starting training...")
    print("=" * 70)
    
    losses = []
    accuracies = []
    best_loss = float('inf')
    best_acc = 0.0
    start_time = time.time()
    
    for epoch in range(num_epochs):
        model.train()
        epoch_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (boards, targets) in enumerate(loader):
            boards, targets = boards.to(device), targets.to(device)
            
            optimizer.zero_grad()
            
            # Forward pass
            # boards: [B, 100] with values 0-4 (board state)
            # But BDH expects vocab indices, and we set V=100
            # So we need to remap board values to valid indices
            
            # Actually, the board values (0-4) are fine as input
            # BDH will embed them
            # The output logits will be [B, T, V=100]
            # We want to predict the target cell (0-99)
            
            logits = model(boards, capture_frames=False)  # [B, T=100, V=100]
            
            # Use last position to predict next cell
            last_logits = logits[:, -1, :]  # [B, V=100]
            
            # Compute loss
            loss = criterion(last_logits, targets)
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            
            epoch_loss += loss.item()
            
            # Calculate accuracy
            preds = last_logits.argmax(dim=-1)
            correct += (preds == targets).sum().item()
            total += targets.size(0)
            
            if batch_idx % 50 == 0:
                elapsed = time.time() - start_time
                acc = 100 * correct / total if total > 0 else 0
                print(f"Epoch {epoch+1:3d}/{num_epochs} | "
                      f"Batch {batch_idx:4d}/{len(loader)} | "
                      f"Loss: {loss.item():.4f} | "
                      f"Acc: {acc:.1f}% | "
                      f"Time: {elapsed/60:.1f}m")
        
        # Epoch summary
        avg_loss = epoch_loss / len(loader)
        accuracy = 100 * correct / total
        losses.append(avg_loss)
        accuracies.append(accuracy)
        
        elapsed = time.time() - start_time
        print(f"\n{'='*70}")
        print(f"Epoch {epoch+1:3d} Complete | "
              f"Avg Loss: {avg_loss:.4f} | "
              f"Accuracy: {accuracy:.2f}% | "
              f"Time: {elapsed/60:.1f}m")
        print(f"{'='*70}\n")
        
        # Save best model
        if accuracy > best_acc:
            best_acc = accuracy
            best_loss = avg_loss
            os.makedirs(checkpoint_dir, exist_ok=True)
            checkpoint_path = os.path.join(checkpoint_dir, 'bdh_pathfinding_trained.pth')
            torch.save(model.state_dict(), checkpoint_path)
            print(f"✅ New best model! Acc: {best_acc:.2f}%, Loss: {best_loss:.4f}\n")
        
        # Early stopping
        if accuracy > 95.0:
            print("🎉 Excellent accuracy achieved! Stopping early.")
            break
    
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print(f"Total time: {(time.time() - start_time)/60:.1f} minutes")
    print(f"Best accuracy: {best_acc:.2f}%")
    print(f"Best loss: {best_loss:.4f}")
    print(f"Checkpoint: {checkpoint_path}")
    print("=" * 70)
    
    # Plot training curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    ax1.plot(losses, linewidth=2, color='#6366f1')
    ax1.set_xlabel('Epoch', fontsize=12)
    ax1.set_ylabel('Loss', fontsize=12)
    ax1.set_title('Training Loss', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(accuracies, linewidth=2, color='#10b981')
    ax2.set_xlabel('Epoch', fontsize=12)
    ax2.set_ylabel('Accuracy (%)', fontsize=12)
    ax2.set_title('Training Accuracy', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = '../../docs/pathfinding_training.png'
    os.makedirs(os.path.dirname(plot_path), exist_ok=True)
    plt.savefig(plot_path, dpi=150)
    print(f"\n✓ Training curves saved: {plot_path}")
    
    return model, losses, accuracies


if __name__ == "__main__":
    print("\n🚀 Starting BDH Pathfinding Training...")
    print("This will train BDH to predict the next cell in an optimal path.\n")
    
    # Train with small dataset first to test
    model, losses, accs = train_bdh_pathfinding(
        num_samples=10000,   # Start small
        num_epochs=50,
        batch_size=32,
        learning_rate=3e-4
    )
    
    print("\n🎉 Training complete!")
    print(f"Final accuracy: {accs[-1]:.2f}%")
    print("\nNext steps:")
    print("1. If accuracy is good (>70%), train on full dataset (50K samples)")
    print("2. Implement inference logic")
    print("3. Integrate into backend API")
