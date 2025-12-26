# 🔄 Reproducibility Guide

**Complete Step-by-Step Guide to Reproduce BDH Brain Explorer**

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation](#installation)
3. [Running the Application](#running-the-application)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)
6. [Common Issues](#common-issues)

---

## System Requirements

### Minimum Requirements

- **Operating System**: macOS 10.15+, Ubuntu 20.04+, or Windows 10+
- **Python**: 3.13 or higher
- **Node.js**: 18.0 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 2GB free space

### Recommended Setup

- **OS**: macOS 13+ or Ubuntu 22.04+
- **Python**: 3.13
- **Node.js**: 20.x LTS
- **RAM**: 16GB
- **GPU**: Optional (CPU works fine)

---

## Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/bdh-brain-explorer.git
cd bdh-brain-explorer
```

### Step 2: Python Environment Setup

#### Option A: Using venv (Recommended)

```bash
# Navigate to reference-bdh directory
cd reference-bdh

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify Python version
python --version  # Should be 3.13+

# Install core dependencies
pip install torch numpy matplotlib networkx pillow

# Install backend dependencies
pip install fastapi uvicorn pydantic requests

# Verify installation
python -c "import torch; print(f'PyTorch {torch.__version__}')"
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"

# Return to project root
cd ..
```

#### Option B: Using conda

```bash
# Create conda environment
conda create -n bdh-explorer python=3.13

# Activate environment
conda activate bdh-explorer

# Install dependencies
pip install torch numpy matplotlib networkx pillow
pip install fastapi uvicorn pydantic requests
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Verify installation
npm list react d3 axios

# Return to project root
cd ..
```

### Step 4: Verify Installation

```bash
# Check Python packages
source reference-bdh/venv/bin/activate
pip list | grep -E "torch|fastapi|numpy|networkx"

# Check Node packages
cd frontend
npm list --depth=0
cd ..
```

**Expected Output**:
```
torch           2.5.1
fastapi         0.127.1
numpy           2.2.2
networkx        3.4.2
```

---

## Running the Application

### Quick Start (Two Terminals)

#### Terminal 1: Backend Server

```bash
# From project root
cd bdh-brain-explorer

# Activate Python environment
source reference-bdh/venv/bin/activate

# Navigate to backend API
cd backend/api

# Start server
python app.py
```

**Expected Output**:
```
============================================================
🚀 Starting BDH Brain Explorer API
============================================================

📦 Loading model...
✓ Model loaded on cpu

✓ Model loaded successfully!

📡 Starting server on http://localhost:8000
📚 API docs available at http://localhost:8000/docs

============================================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

#### Terminal 2: Frontend Development Server

```bash
# From project root
cd bdh-brain-explorer/frontend

# Start development server
npm run dev
```

**Expected Output**:
```
  VITE v7.3.0  ready in 247 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### Access the Application

1. **Frontend**: Open http://localhost:5173/ in your browser
2. **Backend API**: http://localhost:8000/
3. **API Documentation**: http://localhost:8000/docs

---

## Verification

### Step 1: Test Backend API

```bash
# In a new terminal, test the health endpoint
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu",
  "config": {
    "neurons": 2048,
    "layers": 12,
    "heads": 4
  }
}
```

### Step 2: Test Frontend

1. Open http://localhost:5173/
2. You should see the BDH Brain Explorer homepage
3. Click on "Sparse Brain" - should load heatmap visualization
4. Click on "Graph Brain" - should load force-directed graph
5. Click on "Hebbian Animator" - should load synapse animation

### Step 3: Test API Integration

```bash
# Test inference endpoint
curl -X POST http://localhost:8000/api/infer \
  -H "Content-Type: application/json" \
  -d '{"input_tokens": [0,1,2,3,4], "track_states": false}'

# Should return predictions array
```

### Step 4: Verify Visualizations

**Sparse Brain**:
- ✅ Two heatmaps visible (BDH and Transformer)
- ✅ Layer slider works
- ✅ Metrics cards show sparsity percentages
- ✅ Insights panel displays

**Graph Brain**:
- ✅ Force-directed graph renders
- ✅ Nodes are draggable
- ✅ Zoom and pan work
- ✅ Hub neurons highlighted in gold
- ✅ Degree distribution chart visible

**Hebbian Animator**:
- ✅ Synapse strength heatmap displays
- ✅ Play/pause button works
- ✅ Speed slider adjusts animation
- ✅ Layer counter updates
- ✅ Tooltips show on hover

---

## Troubleshooting

### Issue 1: Backend Won't Start

**Symptom**: `ModuleNotFoundError: No module named 'torch'`

**Solution**:
```bash
# Ensure virtual environment is activated
source reference-bdh/venv/bin/activate

# Reinstall dependencies
pip install torch numpy matplotlib networkx pillow fastapi uvicorn pydantic
```

### Issue 2: Frontend Build Errors

**Symptom**: `Cannot find module 'd3'`

**Solution**:
```bash
cd frontend

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
```

### Issue 3: CORS Errors

**Symptom**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**:
- Ensure backend is running on port 8000
- Ensure frontend is running on port 5173
- Check `frontend/.env` has correct API URL:
  ```
  VITE_API_URL=http://localhost:8000
  ```

### Issue 4: Port Already in Use

**Symptom**: `Error: listen EADDRINUSE: address already in use :::8000`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
# Edit backend/api/app.py, change port to 8001
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Issue 5: Graph Brain 500 Error

**Symptom**: `AxiosError: Request failed with status code 500`

**Solution**:
```bash
# Check backend logs for error details
# Usually caused by:
# 1. Backend not running
# 2. Model not loaded
# 3. Missing dependencies

# Restart backend with verbose logging
cd backend/api
python app.py
```

### Issue 6: Slow Performance

**Symptom**: Visualizations lag or freeze

**Solution**:
```bash
# Reduce number of neurons displayed
# Edit frontend/src/components/GraphBrain.tsx
# Change topKNodes prop:
<GraphBrain topKNodes={50} />  # Instead of 100

# Or reduce heatmap resolution
# Edit frontend/src/components/SparseBrain.tsx
# Change maxNeuronsToShow:
const maxNeuronsToShow = 100;  # Instead of 200
```

---

## Common Issues

### Python Version Mismatch

```bash
# Check Python version
python --version

# If wrong version, use python3.13 explicitly
python3.13 -m venv venv
```

### Node Version Issues

```bash
# Check Node version
node --version

# If too old, install latest LTS
# Using nvm:
nvm install --lts
nvm use --lts
```

### Import Errors

```bash
# If you see "cannot import name 'BDH'"
# Ensure you're in the correct directory
cd bdh-brain-explorer
source reference-bdh/venv/bin/activate
cd backend/api
python app.py
```

### TypeScript Errors

```bash
# If frontend shows TypeScript errors
cd frontend

# Reinstall with exact versions
npm install react@19.0.0 react-dom@19.0.0
npm install d3@7.9.0 @types/d3@7.4.3
npm install axios@1.7.9
```

---

## Environment Variables

### Backend

No environment variables required. All configuration is in code.

### Frontend

Create `frontend/.env`:
```bash
VITE_API_URL=http://localhost:8000
```

---

## Testing

### Backend Tests

```bash
# Activate environment
source reference-bdh/venv/bin/activate

# Run instrumentation tests
python test_instrumentation.py

# Run API tests (requires backend running)
python test_api.py
```

### Frontend Tests

```bash
cd frontend

# Type check
npm run type-check

# Build test
npm run build

# Preview production build
npm run preview
```

---

## Production Build

### Backend

```bash
# Backend runs same in production
source reference-bdh/venv/bin/activate
cd backend/api
python app.py
```

### Frontend

```bash
cd frontend

# Build for production
npm run build

# Output in frontend/dist/
# Serve with any static server
npx serve dist
```

---

## Docker (Optional)

### Backend Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY reference-bdh/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/
COPY reference-bdh/ ./reference-bdh/

CMD ["python", "backend/api/app.py"]
```

### Frontend Dockerfile

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .

CMD ["npm", "run", "dev", "--", "--host"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

---

## Performance Optimization

### Backend

```python
# Enable model caching (already implemented)
# Reduce neuron sampling for faster topology extraction
topology = get_topology(threshold=0.1, top_k_nodes=50)
```

### Frontend

```typescript
// Reduce animation complexity
const maxNeuronsToShow = 100;  // Instead of 200

// Increase animation delay for smoother performance
.transition()
  .duration(1000)  // Slower = smoother
  .delay((_, i) => i * 2);  // More delay between cells
```

---

## Verification Checklist

Before submitting, verify:

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:5173/
- [ ] All three modules render correctly
- [ ] API endpoints respond (test with curl)
- [ ] No console errors in browser
- [ ] Visualizations are interactive
- [ ] Documentation is complete
- [ ] Git repository is clean
- [ ] All dependencies listed
- [ ] README is accurate

---

## Support

If you encounter issues not covered here:

1. Check [GitHub Issues](https://github.com/yourusername/bdh-brain-explorer/issues)
2. Review [METHODOLOGY.md](METHODOLOGY.md) for technical details
3. Consult [README.md](README.md) for overview
4. Contact: [your.email@example.com]

---

**Last Updated**: December 26, 2025
**Version**: 1.0.0
**Tested On**: macOS 13, Ubuntu 22.04, Python 3.13, Node 20
