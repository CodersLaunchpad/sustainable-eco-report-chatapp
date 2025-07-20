# Sustainable Eco Chat App with MCP Integration

A microservices-based chat application using Flask backend with Ollama integration, Bootstrap frontend, and MCP (Model Context Protocol) for smart building data analysis and sustainability reporting.

## Architecture

```
sustainable-eco-report-chatapp/
├── backend/          # Main Flask API service (port 5122)
├── frontend/         # Bootstrap web interface (port 3000)
├── mcp-service/      # FastMCP server for data analysis
├── report-service/   # Report generation service (port 5001)
├── dataset/          # building_413_data.csv - Smart home sensor data
├── shared/           # Shared utilities
└── .env             # Environment configuration
```

## Prerequisites

1. **Ollama**: Install Ollama and download the Llama 3.1 model
   ```bash
   # Install Ollama (visit https://ollama.ai for instructions)
   ollama pull llama3.1
   ```

2. **Python 3.8+**: For all backend services
3. **Modern web browser**: For the frontend

## Setup Instructions

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd sustainable-eco-report-chatapp
cp .env.example .env
```

### 2. Install Dependencies for All Services

```bash
# Backend dependencies
. venv/bin/activate && cd backend && pip install -r requirements.txt && cd ..

# MCP Service dependencies
. venve/bin/activate && cd mcp-service && pip install -r requirements.txt && cd ..

# Report Service dependencies
. venve/bin/activate && cd report-service && pip install -r requirements.txt && cd ..
```

### 3. Start All Services (4 Terminals Required)

**Terminal 1 - Start Ollama:**
```bash
ollama serve
```

**Terminal 2 - Start MCP Server:**
```bash
cd mcp-service
python src/server.py
```

**Terminal 3 - Start Report Service:**
```bash
cd report-service
python app.py
```

**Terminal 4 - Start Main Backend:**
```bash
cd backend
python app.py
```

**Terminal 5 - Start Frontend:**
```bash
cd frontend
python -m http.server 3000
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Main Backend API**: http://localhost:5122
- **Report Service**: http://localhost:5001
- **Health Checks**: 
  - Backend: http://localhost:5122/health
  - Report Service: http://localhost:5001/health

## How to Use

### Regular Chat
- Ask any general questions about sustainability
- The AI will respond using Ollama Llama 3.1

### Smart Building Data Reports
The system automatically detects report requests using keywords and generates data-driven sustainability reports from the building sensor dataset.

**Trigger Keywords**: `report`, `analyze`, `sustainability`, `building data`, `environmental`, `co2`, `temperature`, `humidity`, `occupancy`

**Example Queries**:
- "Generate a sustainability report for the building"
- "Analyze the CO2 levels in the building data"
- "Show me environmental comfort analysis"
- "What are the occupancy patterns?"
- "Create a comprehensive sustainability assessment"

### MCP Tools Available
The MCP server provides these data analysis tools:
- **get_data_summary**: Overview of available sensor data
- **analyze_co2_levels**: Air quality and ventilation analysis
- **analyze_occupancy_patterns**: Motion sensor insights for energy optimization
- **get_environmental_comfort_analysis**: Temperature and humidity analysis
- **generate_sustainability_report**: Comprehensive sustainability reports

## Environment Variables

Configure services using `.env` files:

**Main `.env`:**
```env
FLASK_PORT=5122              # Main backend port
FLASK_DEBUG=True             # Debug mode
REPORT_SERVICE_PORT=5001     # Report service port
OLLAMA_URL=http://localhost:11434
MODEL_NAME=llama3.1
```

## API Endpoints

### Main Backend (`localhost:5122`)
- `GET /health` - Health check
- `POST /chat` - Send message to AI (auto-routes to report service for data queries)
- `GET /models` - List available Ollama models

### Report Service (`localhost:5001`)
- `GET /health` - Health check
- `POST /report` - Generate sustainability reports
- `GET /data-summary` - Get building data summary

## Dataset

The application includes `building_413_data.csv` with real smart building sensor data:
- **CO2 levels** (ppm)
- **Temperature** (°C)
- **Humidity** (%)
- **Light levels** (lux)
- **Motion detection** (PIR sensor)
- **Timestamps** and building ID

## Features

- ✅ Responsive Bootstrap UI with report display
- ✅ Real-time chat interface
- ✅ Ollama Llama 3.1 integration
- ✅ **MCP (Model Context Protocol) integration**
- ✅ **Smart building data analysis**
- ✅ **Sustainability report generation**
- ✅ **Data-driven insights and recommendations**
- ✅ Microservices architecture
- ✅ Environment configuration
- ✅ CORS enabled
- ✅ Error handling and fallbacks
- ✅ Typing indicators

## Development

### Adding New MCP Tools
Add new analysis tools in `mcp-service/src/server.py` using the `@mcp.tool()` decorator.

### Customizing Reports
Modify the report generation logic in `report-service/app.py` to customize the LLM prompts and analysis.

### Port Configuration
Update port settings in the respective `.env` files for each service.

## Troubleshooting

1. **Port conflicts**: Check if ports 5122, 5001, 3000 are available
2. **MCP connection issues**: Ensure the MCP service is running before starting the report service
3. **Ollama not responding**: Make sure Ollama is running and llama3.1 model is downloaded
4. **Dataset not found**: Verify `building_413_data.csv` exists in the `dataset/` folder