"""
Test Model-Based Pathfinding Integration

Tests the /api/pathfind-model endpoint with various scenarios.
"""

import requests
import json
import numpy as np

API_URL = "http://localhost:8000"

def create_simple_maze():
    """Create a simple 10x10 maze"""
    board = np.zeros((10, 10), dtype=int)
    
    # Add some walls
    board[2, 1:8] = 1  # Horizontal wall
    board[5, 3:9] = 1  # Another wall
    board[7, 1:6] = 1  # Another wall
    
    # Set start and end
    board[0, 0] = 2  # Start
    board[9, 9] = 3  # End
    
    return board.tolist()

def test_bfs_mode():
    """Test BFS-only mode (baseline)"""
    print("\n" + "="*70)
    print("TEST 1: BFS Mode (Baseline)")
    print("="*70)
    
    board = create_simple_maze()
    
    response = requests.post(
        f"{API_URL}/api/pathfind",
        json={"board": board}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ BFS Solution found: {len(data['solution'])} steps")
        print(f"   Path: {data['solution'][:3]}... → {data['solution'][-3:]}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_model_mode_without_checkpoint():
    """Test model mode when checkpoint doesn't exist"""
    print("\n" + "="*70)
    print("TEST 2: Model Mode (No Checkpoint)")
    print("="*70)
    
    board = create_simple_maze()
    
    response = requests.post(
        f"{API_URL}/api/pathfind-model",
        json={"board": board}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Model Available: {data['model_available']}")
        print(f"Model Error: {data['model_error']}")
        print(f"BFS Solution: {len(data['bfs_solution'])} steps")
        print(f"Fallback Working: {'✅' if data['bfs_solution'] else '❌'}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_model_mode_with_checkpoint():
    """Test model mode when checkpoint exists"""
    print("\n" + "="*70)
    print("TEST 3: Model Mode (With Checkpoint)")
    print("="*70)
    
    board = create_simple_maze()
    
    response = requests.post(
        f"{API_URL}/api/pathfind-model",
        json={"board": board}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Model Available: {data['model_available']}")
        
        if data['model_available']:
            print(f"✅ Model Solution: {data['model_steps']} steps")
            print(f"✅ BFS Solution: {data['bfs_steps']} steps")
            print(f"Solutions Match: {data['solutions_match']}")
            
            if data['solutions_match']:
                print("🎉 PERFECT! Model matches BFS!")
            else:
                print(f"⚠️  Model: {data['model_steps']} steps vs BFS: {data['bfs_steps']} steps")
        else:
            print(f"⚠️  Model not available: {data['model_error']}")
            print(f"✅ Fallback to BFS: {data['bfs_steps']} steps")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_model_status():
    """Test model status endpoint"""
    print("\n" + "="*70)
    print("TEST 4: Model Status")
    print("="*70)
    
    response = requests.get(f"{API_URL}/api/model-status")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Trained Model: {data['is_trained']}")
        print(f"Device: {data['device']}")
        print(f"Expected Sparsity: {data['expected_sparsity']}")
        print(f"Note: {data['note']}")
    else:
        print(f"❌ Error: {response.status_code}")

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 TESTING MODEL-BASED PATHFINDING INTEGRATION")
    print("="*70)
    
    try:
        # Test 1: BFS baseline
        test_bfs_mode()
        
        # Test 2: Model mode without checkpoint
        test_model_mode_without_checkpoint()
        
        # Test 3: Model mode with checkpoint (if available)
        test_model_mode_with_checkpoint()
        
        # Test 4: Model status
        test_model_status()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETE")
        print("="*70)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print("   Make sure the backend server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    run_all_tests()
