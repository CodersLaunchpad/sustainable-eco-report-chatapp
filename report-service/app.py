#!/usr/bin/env python3
"""
Report Generation Service
Integrates with MCP server to generate sustainability reports using LLM
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import asyncio
from mcp_use import MCPClient

load_dotenv('../.env', override=True)

app = Flask(__name__)
CORS(app)

# Configuration
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
MODEL_NAME = os.getenv('MODEL_NAME', 'llama3.1')

class ReportGenerator:
    def __init__(self):
        self.mcp_client = None
        self.mcp_config = {
            "mcpServers": {
                "smart_home_data": {
                    "command": "python",
                    "args": [os.path.abspath("../mcp-service/src/server.py")],
                    "cwd": os.path.abspath("../mcp-service")
                }
            }
        }
    
    async def get_mcp_client(self):
        """Initialize MCP client connection"""
        if self.mcp_client is None:
            self.mcp_client = MCPClient.from_dict(self.mcp_config)
            await self.mcp_client.connect()
        return self.mcp_client
    
    async def get_building_data_summary(self):
        """Get data summary from MCP server"""
        try:
            client = await self.get_mcp_client()
            result = await client.call_tool("smart_home_data", "get_data_summary", {})
            return json.loads(result.content[0].text) if result.content else None
        except Exception as e:
            print(f"Error getting data summary: {e}")
            return None
    
    async def analyze_sustainability_data(self, analysis_type="comprehensive"):
        """Get sustainability analysis from MCP server"""
        try:
            client = await self.get_mcp_client()
            
            if analysis_type == "co2":
                result = await client.call_tool("smart_home_data", "analyze_co2_levels", {})
            elif analysis_type == "occupancy":
                result = await client.call_tool("smart_home_data", "analyze_occupancy_patterns", {})
            elif analysis_type == "comfort":
                result = await client.call_tool("smart_home_data", "get_environmental_comfort_analysis", {})
            else:  # comprehensive
                result = await client.call_tool("smart_home_data", "generate_sustainability_report", {"report_type": "comprehensive"})
            
            return json.loads(result.content[0].text) if result.content else None
        except Exception as e:
            print(f"Error analyzing data: {e}")
            return None
    
    def generate_llm_report(self, data_analysis, user_query):
        """Generate human-readable report using LLM"""
        try:
            # Prepare context for LLM
            context = f"""
            You are a sustainability expert analyzing smart building data. 
            Based on the following data analysis, provide insights and recommendations:
            
            Data Analysis:
            {json.dumps(data_analysis, indent=2)}
            
            User Query: {user_query}
            
            Please provide:
            1. A clear summary of the building's sustainability performance
            2. Key environmental insights from the sensor data
            3. Specific recommendations for improving energy efficiency
            4. Actions to enhance occupant comfort while reducing environmental impact
            5. Metrics and benchmarks for tracking progress
            
            Format your response as a professional sustainability report with clear sections and actionable recommendations.
            """
            
            # Call Ollama
            ollama_payload = {
                "model": MODEL_NAME,
                "prompt": context,
                "stream": False
            }
            
            response = requests.post(f"{OLLAMA_URL}/api/generate", json=ollama_payload, timeout=60)
            
            if response.status_code == 200:
                ollama_response = response.json()
                return ollama_response.get('response', '')
            else:
                return "Error generating LLM report"
                
        except Exception as e:
            print(f"Error generating LLM report: {e}")
            return f"Error generating report: {str(e)}"

# Global report generator instance
report_generator = ReportGenerator()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "report-service"})

@app.route('/report', methods=['POST'])
def generate_report():
    """Generate sustainability report based on user request"""
    try:
        data = request.get_json()
        user_query = data.get('query', 'Generate a comprehensive sustainability report')
        report_type = data.get('type', 'comprehensive')
        
        # Run async operations in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get data analysis from MCP server
            data_analysis = loop.run_until_complete(
                report_generator.analyze_sustainability_data(report_type)
            )
            
            if not data_analysis:
                return jsonify({
                    "error": "Failed to analyze building data",
                    "status": "error"
                }), 500
            
            # Generate human-readable report using LLM
            llm_report = report_generator.generate_llm_report(data_analysis, user_query)
            
            # Combine structured data with LLM insights
            report_response = {
                "status": "success",
                "generated_at": datetime.now().isoformat(),
                "report_type": report_type,
                "user_query": user_query,
                "llm_analysis": llm_report,
                "structured_data": data_analysis,
                "summary": {
                    "data_points_analyzed": data_analysis.get("report_metadata", {}).get("total_records_analyzed", 0) if "report_metadata" in data_analysis else "N/A",
                    "sustainability_score": data_analysis.get("executive_summary", {}).get("overall_sustainability_score", "N/A") if "executive_summary" in data_analysis else "N/A",
                    "key_recommendations": data_analysis.get("recommendations", [])[:3] if "recommendations" in data_analysis else []
                }
            }
            
            return jsonify(report_response)
            
        finally:
            loop.close()
            
    except Exception as e:
        print(f"Error generating report: {e}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e),
            "status": "error"
        }), 500

@app.route('/data-summary', methods=['GET'])
def get_data_summary():
    """Get summary of available building data"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            summary = loop.run_until_complete(
                report_generator.get_building_data_summary()
            )
            
            if summary:
                return jsonify({
                    "status": "success",
                    "data": summary
                })
            else:
                return jsonify({
                    "error": "Failed to get data summary",
                    "status": "error"
                }), 500
                
        finally:
            loop.close()
            
    except Exception as e:
        print(f"Error getting data summary: {e}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e),
            "status": "error"
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('REPORT_SERVICE_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    print(f"Starting Report Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)