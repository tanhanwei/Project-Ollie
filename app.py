import random
from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

import logging
from manager.agent_manager import AgentManager
from extensions import socketio

app = Flask(__name__)
socketio.init_app(app)

agent_manager = AgentManager()

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('gemini-client/build', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('gemini-client/build', path)

@app.route('/create-manager', methods=['POST']) 
def create_manager():
    agent_manager = AgentManager()
    return jsonify({'response': 'Manager created'}), 200


@app.route('/get-agents', methods=['POST'])
def get_agents():
    agents = agent_manager.get_all_agents()
    return jsonify({'agents': agents}), 200

@app.route('/api', methods=['POST'])
def get_response():
    data = request.get_json(force=True, silent=True, cache=False)
    socketio.emit('debug', {'message': f"Received Data: {data}"})  # Emit debug info
    
    user_input = data.get("input")
    agent_keys = data.get("agent_keys", [])  # Default to empty list if not provided
    
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    
    agent_manager.set_agents(agent_keys)

    try:
        response = agent_manager.generate_response(user_input)
        return jsonify({'response': response}), 200
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def test_connect():
    emit('after connect',  {'data':'Let\'s communicate!'})

if __name__ == "__main__":
    app.run(debug=True)  # Set debug=False in a production environment
    socketio.run(app)
