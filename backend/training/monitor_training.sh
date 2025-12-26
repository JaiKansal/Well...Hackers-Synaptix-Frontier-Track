#!/bin/bash
# Monitor training progress

echo "🔍 Monitoring BDH Pathfinding Training..."
echo "========================================"
echo ""

# Check if process is running
if ps aux | grep -q "[t]rain_pathfinding_simple.py"; then
    echo "✅ Training process is RUNNING"
    
    # Get process info
    ps aux | grep "[t]rain_pathfinding_simple.py" | awk '{print "   PID:", $2, "| CPU:", $3"%", "| Memory:", $4"%", "| Time:", $10}'
    
    echo ""
    echo "📊 Waiting for output..."
    echo "   (Dataset generation may take 5-10 minutes for 10K samples)"
    echo ""
    
    # Check for checkpoint
    if [ -f "../../checkpoints/bdh_pathfinding_trained.pth" ]; then
        echo "✅ Checkpoint found!"
        ls -lh ../../checkpoints/bdh_pathfinding_trained.pth
    else
        echo "⏳ No checkpoint yet (training in progress)"
    fi
    
    echo ""
    echo "💡 Tip: Training output may be buffered. Check back in 5-10 minutes."
    
else
    echo "❌ Training process NOT running"
    echo ""
    echo "Check if it completed or failed:"
    echo "   - Look for checkpoint in checkpoints/"
    echo "   - Check for error logs"
fi

echo ""
echo "========================================"
