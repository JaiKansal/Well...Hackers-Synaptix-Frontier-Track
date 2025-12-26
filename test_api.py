"""
Test FastAPI Backend

This script tests all API endpoints to ensure they're working correctly.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_root():
    """Test root endpoint"""
    print_section("TEST 1: Root Endpoint")
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✓ Root endpoint working")

def test_health():
    """Test health check endpoint"""
    print_section("TEST 2: Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert data['status'] == 'healthy'
    assert data['model_loaded'] == True
    print("✓ Health check passed")

def test_config():
    """Test config endpoint"""
    print_section("TEST 3: Model Configuration")
    
    response = requests.get(f"{BASE_URL}/api/config")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Configuration:")
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    assert response.status_code == 200
    print("✓ Config endpoint working")

def test_inference():
    """Test inference endpoint"""
    print_section("TEST 4: BDH Inference")
    
    # Test with small input
    payload = {
        "input_tokens": [0, 1, 2, 3, 4, 0, 1, 2, 3, 4],
        "track_states": False  # Don't track states for speed
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/infer", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Predictions length: {len(data['predictions'])}")
        print(f"Predictions: {data['predictions'][:10]}...")
        print("✓ Inference working")
    else:
        print(f"Error: {response.text}")
        raise Exception("Inference failed")

def test_inference_with_states():
    """Test inference with state tracking"""
    print_section("TEST 5: Inference with State Tracking")
    
    payload = {
        "input_tokens": [0, 1, 2, 3, 4],
        "track_states": True
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    print("Running inference (this may take a moment)...")
    
    response = requests.post(f"{BASE_URL}/api/infer", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Predictions: {data['predictions']}")
        print(f"Sparsity:")
        print(f"  Y mean: {data['sparsity']['y_sparsity_mean']:.4f}")
        print(f"  Y std: {data['sparsity']['y_sparsity_std']:.4f}")
        print(f"  X mean: {data['sparsity']['x_sparsity_mean']:.4f}")
        print(f"States captured: {list(data['states'].keys())}")
        print("✓ State tracking working")
    else:
        print(f"Error: {response.text}")
        raise Exception("Inference with states failed")

def test_topology():
    """Test topology endpoint"""
    print_section("TEST 6: Graph Topology")
    
    # Test with threshold and top_k
    params = {
        "threshold": 0.05,
        "top_k_nodes": 50
    }
    
    print(f"Parameters: {json.dumps(params, indent=2)}")
    
    response = requests.get(f"{BASE_URL}/api/topology", params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Nodes: {len(data['nodes'])}")
        print(f"Edges: {len(data['edges'])}")
        print(f"Metrics:")
        for key, value in data['metrics'].items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            elif isinstance(value, list):
                print(f"  {key}: {len(value)} items")
            else:
                print(f"  {key}: {value}")
        print("✓ Topology extraction working")
    else:
        print(f"Error: {response.text}")
        raise Exception("Topology extraction failed")

def test_sparsity():
    """Test sparsity measurement endpoint"""
    print_section("TEST 7: Sparsity Measurement")
    
    payload = {
        "input_tokens": [0, 1, 2, 3, 4, 0, 1, 2, 3, 4],
        "track_states": True
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/sparsity", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Y Sparsity:")
        print(f"  Mean: {data['y_sparsity_mean']:.4f}")
        print(f"  Std: {data['y_sparsity_std']:.4f}")
        print(f"  Range: [{data['y_sparsity_min']:.4f}, {data['y_sparsity_max']:.4f}]")
        print(f"  Per layer: {len(data['y_sparsity_per_layer'])} values")
        print(f"X Sparsity:")
        print(f"  Mean: {data['x_sparsity_mean']:.4f}")
        print(f"  Std: {data['x_sparsity_std']:.4f}")
        print("✓ Sparsity measurement working")
    else:
        print(f"Error: {response.text}")
        raise Exception("Sparsity measurement failed")

def test_pathfinding():
    """Test pathfinding endpoint"""
    print_section("TEST 8: Pathfinding")
    
    # Create a simple 4x4 board
    # 0=FLOOR, 1=WALL, 2=START, 3=END
    board = [
        [0, 0, 1, 0],
        [2, 0, 1, 0],
        [0, 0, 0, 3],
        [0, 1, 0, 0]
    ]
    
    payload = {"board": board}
    
    print(f"Input board:")
    for row in board:
        print(f"  {row}")
    
    print("\nRunning pathfinding (this may take a moment)...")
    
    response = requests.post(f"{BASE_URL}/api/pathfind", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nPredicted board:")
        for row in data['predicted_board']:
            print(f"  {row}")
        print(f"\nSparsity:")
        print(f"  Y avg: {data['sparsity']['y_avg']:.4f}")
        print(f"  X avg: {data['sparsity']['x_avg']:.4f}")
        print(f"Attention flow: {len(data['attention_flow']['edges_per_layer'])} layers")
        print("✓ Pathfinding working")
    else:
        print(f"Error: {response.text}")
        raise Exception("Pathfinding failed")

def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*60)
    print("  🧪 Testing BDH Brain Explorer API")
    print("="*60)
    
    print("\n⏳ Waiting for server to start...")
    time.sleep(2)
    
    try:
        # Test each endpoint
        test_root()
        test_health()
        test_config()
        test_inference()
        test_inference_with_states()
        test_topology()
        test_sparsity()
        test_pathfinding()
        
        # Summary
        print("\n" + "="*60)
        print("  ✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n📊 Summary:")
        print("  ✓ Root endpoint")
        print("  ✓ Health check")
        print("  ✓ Model configuration")
        print("  ✓ BDH inference")
        print("  ✓ State tracking")
        print("  ✓ Graph topology")
        print("  ✓ Sparsity measurement")
        print("  ✓ Pathfinding")
        print("\n🎉 FastAPI backend is fully functional!")
        print("\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print("Make sure the server is running on http://localhost:8000")
        print("\nTo start the server, run:")
        print("  cd backend/api && python app.py")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise

if __name__ == "__main__":
    run_all_tests()
