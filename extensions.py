import logging
from flask_socketio import SocketIO

# Create the SocketIO instance without initializing it with the Flask app
socketio = SocketIO()

def emit_debug_message(message, agent_name):
        try:
            socketio.emit('debug', {'message': message, 'agent': agent_name})
        except Exception as e:
            print(f"Error emitting debug message: {e}")
            logging.error(f"Error emitting debug message: {e}")
            return
