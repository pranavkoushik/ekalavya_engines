from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.agent_coordinator import AgentCoordinator
import os
from config import GEMINI_API_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS

app = Flask(__name__)
CORS(app)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize agent coordinator
coordinator = AgentCoordinator(GEMINI_API_KEY)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/analyze_dataset', methods=['POST'])
def analyze_dataset_api():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save file temporarily
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(temp_path)
        
        # Process dataset
        result = coordinator.process_dataset(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query_dataset', methods=['POST'])
def query_dataset_api():
    try:
        data = request.json
        if not data or 'query' not in data or 'dataset_id' not in data:
            return jsonify({'error': 'Missing query or dataset_id'}), 400
        
        result = coordinator.analyze_query(data['query'], data['dataset_id'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dataset/<int:dataset_id>/history', methods=['GET'])
def get_dataset_history(dataset_id):
    try:
        result = coordinator.get_analysis_history(dataset_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.teardown_appcontext
def cleanup(error):
    coordinator.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
