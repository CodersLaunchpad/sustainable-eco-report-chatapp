# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a microservices-based chat application with MCP (Model Context Protocol) integration for smart building data analysis. The system consists of four main services:

1. **Main Backend** (`backend/app.py`, port 5122): Flask API that routes between regular chat (via Ollama) and report requests (via report service). Uses keyword detection to identify report requests.

2. **Report Service** (`report-service/app.py`, port 5001): Generates sustainability reports by directly importing MCP server functions and calling Ollama for LLM analysis. Uses direct function imports rather than MCP protocol due to mcp-use library complexity.

3. **MCP Service** (`mcp-service/src/server.py`): FastMCP server providing data analysis tools using pandas/numpy on building sensor data. Functions are decorated with `@mcp.tool()` but are also directly importable.

4. **Frontend** (`frontend/`, port 3000): Bootstrap-based chat interface that detects report responses and displays them with special styling.

## Key Development Commands

### Environment Setup
```bash
# Activate virtual environment (required for all commands)
source venv/bin/activate

# Install dependencies for all services
cd backend && pip install -r requirements.txt && cd ..
cd mcp-service && pip install setuptools wheel && pip install -r requirements.txt && cd ..
cd report-service && pip install -r requirements.txt && cd ..
```

### Starting All Services (5 terminals required)
```bash
# Terminal 1: Ollama (prerequisite)
ollama serve

# Terminal 2: MCP Server
cd mcp-service && python src/server.py

# Terminal 3: Report Service
cd report-service && python app.py

# Terminal 4: Main Backend
cd backend && python app.py

# Terminal 5: Frontend
cd frontend && python -m http.server 3000
```

### Environment Configuration
- Main configuration in `.env` (use `FLASK_PORT=5122` due to macOS AirPlay conflict)
- Each service has its own `.env` file
- Critical: Use `load_dotenv('.env', override=True)` to override system environment variables

## Data Flow Architecture

**Regular Chat Flow:**
User → Frontend → Main Backend → Ollama → Response

**Report Generation Flow:**
User → Frontend → Main Backend (keyword detection) → Report Service → MCP Functions (direct import) → Ollama → Enhanced Report Response

## Important Implementation Details

### MCP Integration Pattern
- Originally designed to use mcp-use library with MCPClient, but this proved complex
- **Current approach**: Report service directly imports MCP server functions using `sys.path.append()`
- MCP functions are FastMCP tool objects; access underlying function via `.fn` attribute if needed
- Dataset loading happens once during ReportGenerator initialization

### Environment Variable Handling
- **Critical**: Use `load_dotenv('.env', override=True)` in Flask apps
- System environment variables (like `FLASK_PORT=5000`) can override .env files without override=True
- Port 5000 conflicts with macOS AirPlay; use 5122 for main backend

### Frontend Report Detection
- Backend uses keyword array: `['report', 'analyze', 'sustainability', 'building data', 'environmental', 'co2', 'temperature', 'humidity', 'occupancy']`
- Report responses get special UI treatment with score badges, recommendations, and action buttons

### Dataset Structure
- Located at `dataset/building_413_data.csv`
- Contains real smart building sensor data: CO2, temperature, humidity, light, PIR motion
- Loaded once by MCP service functions using pandas

## Common Development Tasks

### Adding New MCP Analysis Tools
1. Add function to `mcp-service/src/server.py` with `@mcp.tool()` decorator
2. Import in `report-service/app.py` ReportGenerator.__init__
3. Add to mapping in `analyze_sustainability_data()` method

### Modifying Report Keywords
Update `report_keywords` array in `backend/app.py` chat route

### Debugging Service Communication
- Check health endpoints: `/health` on ports 5122 and 5001
- Report service imports MCP functions directly, not via network calls
- Frontend connects to main backend only (port 5122)

### Port Configuration
- Main backend: `FLASK_PORT` in `.env` (default 5122)
- Report service: `REPORT_SERVICE_PORT` in `.env` (default 5001)
- Frontend: Start with `python -m http.server 3000`
- MCP service: Standalone, no web interface

## Dataset Analysis Capabilities

The MCP service provides these analysis functions:
- `get_data_summary()`: Basic dataset statistics
- `analyze_co2_levels()`: Air quality analysis with date filtering
- `analyze_occupancy_patterns()`: Motion sensor pattern analysis
- `get_environmental_comfort_analysis()`: Temperature/humidity comfort metrics
- `generate_sustainability_report()`: Comprehensive sustainability assessment