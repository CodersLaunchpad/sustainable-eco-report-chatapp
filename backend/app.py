from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv('.env', override=True)

app = Flask(__name__)
CORS(app)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1"
REPORT_SERVICE_URL = "http://localhost:5001"

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "chat-backend"})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400
        
        # Check if this is a report request
        report_keywords = ['report', 'analyze', 'sustainability', 'building data', 'environmental', 'co2', 'temperature', 'humidity', 'occupancy']
        is_report_request = any(keyword in user_message.lower() for keyword in report_keywords)
        
        if is_report_request:
            try:
                # Forward to report service
                report_payload = {
                    "query": user_message,
                    "type": "comprehensive"
                }
                
                report_response = requests.post(f"{REPORT_SERVICE_URL}/report", 
                                              json=report_payload, timeout=60)
                
                if report_response.status_code == 200:
                    report_data = report_response.json()
                    return jsonify({
                        "message": report_data.get('llm_analysis', 'Report generated successfully'),
                        "model": MODEL_NAME,
                        "status": "success",
                        "type": "report",
                        "report_data": report_data
                    })
                else:
                    # Fallback to regular chat if report service fails
                    pass
                    
            except Exception as e:
                print(f"Report service error: {e}")
                # Fallback to regular chat
                pass
        
        # Regular chat functionality
        ollama_payload = {
            "model": MODEL_NAME,
            "prompt": user_message,
            "stream": False
        }
        
        response = requests.post(OLLAMA_URL, json=ollama_payload, timeout=30)
        
        if response.status_code == 200:
            ollama_response = response.json()
            ai_message = ollama_response.get('response', '')
            return jsonify({
                "message": ai_message,
                "model": MODEL_NAME,
                "status": "success",
                "type": "chat"
            })
        else:
            return jsonify({
                "error": "Failed to get response from Ollama",
                "status_code": response.status_code
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Connection error to Ollama service",
            "details": str(e)
        }), 503
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@app.route('/validate-report', methods=['POST'])
def validate_report():
    try:
        data = request.get_json()
        report_text = data.get('report_text', '')
        report_data = data.get('report_data', {})
        
        if not report_text:
            return jsonify({"error": "Report text is required"}), 400
        
        # Forward to report service for validation
        validation_payload = {
            "report_text": report_text,
            "report_data": report_data
        }
        
        validation_response = requests.post(f"{REPORT_SERVICE_URL}/validate", 
                                          json=validation_payload, timeout=30)
        
        if validation_response.status_code == 200:
            validation_result = validation_response.json()
            return jsonify(validation_result)
        else:
            return jsonify({
                "error": "Failed to validate report",
                "status_code": validation_response.status_code
            }), validation_response.status_code
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": "Connection error to validation service",
            "details": str(e)
        }), 503
    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@app.route('/models', methods=['GET'])
def get_models():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to fetch models"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)