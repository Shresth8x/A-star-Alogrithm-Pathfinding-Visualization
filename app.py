"""
Flask web application for interactive A* pathfinding visualization.
Provides REST API and WebSocket support for real-time algorithm streaming.
"""

import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time

from src.coordinate_parser import parse_full_coordinate, CoordinateParseError, validate_coordinates
from src.map_data import MapDataManager, CityMap
from src.astar_streaming import (
    astar_step_generator,
    get_node_coordinates,
    get_graph_edges_geojson,
    get_path_geojson
)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'astar-pathfinding-secret-key'
CORS(app)

# Initialize SocketIO with eventlet
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize map data manager
map_manager = MapDataManager(cache_dir="cache")

# Global state for current session
current_session = {
    'city_map': None,
    'graph': None,
    'start_node': None,
    'goal_node': None,
    'generator': None,
    'is_running': False,
    'speed': 1.0,  # Speed multiplier
    'previous_open_set': set(),  # Track previous state for delta updates
    'previous_closed_set': set(),  # Track previous state for delta updates
    'message_batch': [],  # Batch messages before sending
    'batch_size': 5  # Number of steps to batch together
}


@app.route('/')
def index():
    """Serve the main HTML interface."""
    return render_template('index.html')


@app.route('/api/parse-coordinates', methods=['POST'])
def parse_coordinates():
    """
    Parse DMS coordinate strings to decimal degrees.

    Expected JSON body:
    {
        "start": "16°17'02.6\"N 80°27'15.1\"E",
        "end": "16°17'30.0\"N 80°27'45.0\"E"
    }

    Returns:
    {
        "success": true,
        "start": {"lat": 16.284056, "lon": 80.454194},
        "end": {"lat": 16.291667, "lon": 80.4625}
    }
    """
    try:
        data = request.json
        start_str = data.get('start', '')
        end_str = data.get('end', '')

        if not start_str or not end_str:
            return jsonify({
                'success': False,
                'error': 'Both start and end coordinates are required'
            }), 400

        # Parse coordinates
        start_lat, start_lon = parse_full_coordinate(start_str)
        end_lat, end_lon = parse_full_coordinate(end_str)

        # Validate
        if not validate_coordinates(start_lat, start_lon):
            return jsonify({
                'success': False,
                'error': f'Invalid start coordinates: {start_lat}, {start_lon}'
            }), 400

        if not validate_coordinates(end_lat, end_lon):
            return jsonify({
                'success': False,
                'error': f'Invalid end coordinates: {end_lat}, {end_lon}'
            }), 400

        return jsonify({
            'success': True,
            'start': {'lat': start_lat, 'lon': start_lon},
            'end': {'lat': end_lat, 'lon': end_lon}
        })

    except CoordinateParseError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500


@app.route('/api/load-map', methods=['POST'])
def load_map():
    """
    Load map data for given coordinates.

    Expected JSON body:
    {
        "start_lat": 16.284056,
        "start_lon": 80.454194,
        "end_lat": 16.291667,
        "end_lon": 80.4625
    }

    Returns:
    {
        "success": true,
        "map_info": {...},
        "edges": [...],
        "bounds": [[min_lat, min_lon], [max_lat, max_lon]]
    }
    """
    try:
        data = request.json
        start_lat = data.get('start_lat')
        start_lon = data.get('start_lon')
        end_lat = data.get('end_lat')
        end_lon = data.get('end_lon')

        if None in [start_lat, start_lon, end_lat, end_lon]:
            return jsonify({
                'success': False,
                'error': 'Missing coordinate parameters'
            }), 400

        # Load the full Varanasi city map (use full cached map instead of route-specific subset)
        # This ensures pathfinding has access to all roads in the city
        city_map = map_manager.get_varanasi_city(use_cache=True)

        # Find nearest nodes in the full city map
        start_node = map_manager.find_nearest_node(city_map, start_lat, start_lon)
        goal_node = map_manager.find_nearest_node(city_map, end_lat, end_lon)

        # Get actual coordinates of nearest nodes
        actual_start = map_manager.get_node_coordinates(city_map, start_node)
        actual_goal = map_manager.get_node_coordinates(city_map, goal_node)

        # Store in session
        current_session['city_map'] = city_map
        current_session['graph'] = city_map.graph
        current_session['start_node'] = start_node
        current_session['goal_node'] = goal_node

        # Convert edges to GeoJSON
        edges = get_graph_edges_geojson(city_map.graph)

        # Calculate bounds
        north, south, east, west = city_map.bbox

        return jsonify({
            'success': True,
            'map_info': {
                'name': city_map.name,
                'nodes': city_map.graph.number_of_nodes(),
                'edges': city_map.graph.number_of_edges(),
                'start_node': start_node,
                'goal_node': goal_node,
                'actual_start': {'lat': actual_start[0], 'lon': actual_start[1]},
                'actual_goal': {'lat': actual_goal[0], 'lon': actual_goal[1]}
            },
            'edges': edges,
            'bounds': [[south, west], [north, east]]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to load map: {str(e)}'
        }), 500


@app.route('/api/load-guntur-map', methods=['POST'])
def load_guntur_map():
    """
    Load map data for Guntur city.

    Returns:
    {
        "success": true,
        "map_info": {...},
        "edges": [...],
        "bounds": [[min_lat, min_lon], [max_lat, max_lon]]
    }
    """
    try:
        # Load Guntur city map
        city_map = map_manager.get_guntur_city(use_cache=True)

        # Store in session (without start/goal nodes for now)
        current_session['city_map'] = city_map
        current_session['graph'] = city_map.graph
        current_session['start_node'] = None
        current_session['goal_node'] = None

        # Convert edges to GeoJSON
        edges = get_graph_edges_geojson(city_map.graph)

        # Calculate bounds
        north, south, east, west = city_map.bbox

        return jsonify({
            'success': True,
            'map_info': {
                'name': city_map.name,
                'nodes': city_map.graph.number_of_nodes(),
                'edges': city_map.graph.number_of_edges()
            },
            'edges': edges,
            'bounds': [[south, west], [north, east]]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to load Guntur map: {str(e)}'
        }), 500


@app.route('/api/load-varanasi-map', methods=['POST'])
def load_varanasi_map():
    """
    Load map data for Varanasi city.

    Returns:
    {
        "success": true,
        "map_info": {...},
        "edges": [...],
        "bounds": [[min_lat, min_lon], [max_lat, max_lon]]
    }
    """
    try:
        # Load Varanasi city map
        city_map = map_manager.get_varanasi_city(use_cache=True)

        # Store in session (without start/goal nodes for now)
        current_session['city_map'] = city_map
        current_session['graph'] = city_map.graph
        current_session['start_node'] = None
        current_session['goal_node'] = None

        # Convert edges to GeoJSON
        edges = get_graph_edges_geojson(city_map.graph)

        # Calculate bounds
        north, south, east, west = city_map.bbox

        return jsonify({
            'success': True,
            'map_info': {
                'name': city_map.name,
                'nodes': city_map.graph.number_of_nodes(),
                'edges': city_map.graph.number_of_edges()
            },
            'edges': edges,
            'bounds': [[south, west], [north, east]]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to load Varanasi map: {str(e)}'
        }), 500


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('connected', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')
    current_session['is_running'] = False


@socketio.on('start_pathfinding')
def handle_start_pathfinding(data):
    """
    Start the A* pathfinding algorithm and stream results.

    Expected data:
    {
        "speed": 1.0  // Speed multiplier (0.5 to 5.0)
    }
    """
    if current_session['graph'] is None:
        emit('error', {'message': 'No map loaded. Please load a map first.'})
        return

    if current_session['start_node'] is None or current_session['goal_node'] is None:
        emit('error', {'message': 'Start or goal node not set.'})
        return

    # Set speed
    speed = data.get('speed', 1.0)
    current_session['speed'] = max(0.1, min(5.0, speed))

    # Create generator
    generator = astar_step_generator(
        current_session['graph'],
        current_session['start_node'],
        current_session['goal_node']
    )

    current_session['generator'] = generator
    current_session['is_running'] = True

    # Start streaming
    stream_algorithm_steps()


@socketio.on('pause_pathfinding')
def handle_pause_pathfinding():
    """Pause the pathfinding algorithm."""
    current_session['is_running'] = False
    emit('paused', {'status': 'paused'})


@socketio.on('resume_pathfinding')
def handle_resume_pathfinding():
    """Resume the pathfinding algorithm."""
    if current_session['generator'] is None:
        emit('error', {'message': 'No algorithm in progress.'})
        return

    current_session['is_running'] = True
    stream_algorithm_steps()


@socketio.on('reset_pathfinding')
def handle_reset_pathfinding():
    """Reset the pathfinding visualization."""
    current_session['is_running'] = False
    current_session['generator'] = None
    emit('reset', {'status': 'reset'})


@socketio.on('set_speed')
def handle_set_speed(data):
    """
    Set the visualization speed.

    Expected data:
    {
        "speed": 1.0  // Speed multiplier (0.5 to 5.0)
    }
    """
    speed = data.get('speed', 1.0)
    current_session['speed'] = max(0.1, min(5.0, speed))
    emit('speed_updated', {'speed': current_session['speed']})


def stream_algorithm_steps():
    """Stream A* algorithm steps to the client via WebSocket."""
    if current_session['generator'] is None:
        return

    # Reset previous state tracking and batch
    current_session['previous_open_set'] = set()
    current_session['previous_closed_set'] = set()
    current_session['message_batch'] = []

    try:
        while current_session['is_running']:
            # Get next step
            try:
                state_type, state_data = next(current_session['generator'])
            except StopIteration:
                # Send any remaining batched messages
                if 'message_batch' in current_session and current_session['message_batch']:
                    socketio.emit('algorithm_step_batch', current_session['message_batch'])
                    current_session['message_batch'] = []

                # Algorithm completed
                current_session['is_running'] = False
                current_session['generator'] = None
                return

            # Get current sets
            current_open_set = set(state_data.get('open_set', set()))
            current_closed_set = set(state_data.get('closed_set', set()))

            # Calculate deltas (only send nodes that changed)
            # Initialize previous sets if not exists
            if 'previous_open_set' not in current_session:
                current_session['previous_open_set'] = set()
            if 'previous_closed_set' not in current_session:
                current_session['previous_closed_set'] = set()

            open_set_added = list(current_open_set - current_session['previous_open_set'])
            open_set_removed = list(current_session['previous_open_set'] - current_open_set)
            closed_set_added = list(current_closed_set - current_session['previous_closed_set'])

            # Update previous state
            current_session['previous_open_set'] = current_open_set.copy()
            current_session['previous_closed_set'] = current_closed_set.copy()

            # Build optimized serializable data (delta-based, no coordinates)
            serializable_data = {
                'state_type': state_type,
                'open_set_added': open_set_added,  # Only new nodes
                'open_set_removed': open_set_removed,  # Only removed nodes
                'closed_set_added': closed_set_added,  # Only new nodes
                'current': state_data.get('current'),  # Just node ID (no coordinates)
                'nodes_explored': state_data.get('nodes_explored', 0),
                'g_score': state_data.get('g_score', 0),
                'f_score': state_data.get('f_score', 0),
                'start_node': state_data.get('start_node'),
                'goal_node': state_data.get('goal_node')
            }

            # Add path data if available
            if 'path_so_far' in state_data:
                path = state_data['path_so_far']
                if path and len(path) > 1:
                    path_geojson = get_path_geojson(current_session['graph'], path)
                    serializable_data['path_so_far'] = path_geojson

            if state_type == 'found_path':
                path = state_data.get('path', [])
                path_geojson = get_path_geojson(current_session['graph'], path)
                serializable_data['path'] = path_geojson
                serializable_data['path_length'] = state_data.get('path_length', 0)
                # Send immediately on completion
                socketio.emit('algorithm_step', serializable_data)
                # Reset batch state
                if 'message_batch' in current_session:
                    current_session['message_batch'] = []
                return

            if state_type == 'no_path':
                # Send immediately on failure
                socketio.emit('algorithm_step', serializable_data)
                # Reset batch state
                if 'message_batch' in current_session:
                    current_session['message_batch'] = []
                return

            # Removed coordinate serialization - frontend will compute from node IDs
            # This reduces payload size significantly (60-80% reduction)

            # Initialize message batch if not exists
            if 'message_batch' not in current_session:
                current_session['message_batch'] = []
            if 'batch_size' not in current_session:
                current_session['batch_size'] = 5

            # Add to batch instead of sending immediately
            current_session['message_batch'].append(serializable_data)

            # Send batch when it reaches the configured size
            if len(current_session['message_batch']) >= current_session['batch_size']:
                socketio.emit('algorithm_step_batch', current_session['message_batch'])
                current_session['message_batch'] = []

            # Calculate delay based on speed
            base_delay = 0.1  # 100ms base delay
            delay = base_delay / current_session['speed']
            socketio.sleep(delay)

        # Send any remaining batched messages when paused/stopped
        if 'message_batch' in current_session and current_session['message_batch']:
            socketio.emit('algorithm_step_batch', current_session['message_batch'])
            current_session['message_batch'] = []

    except Exception as e:
        print(f"Error in stream_algorithm_steps: {e}")
        socketio.emit('error', {'message': f'Algorithm error: {str(e)}'})
        current_session['is_running'] = False
        current_session['generator'] = None
        # Clear batch on error
        if 'message_batch' in current_session:
            current_session['message_batch'] = []


if __name__ == '__main__':
    # Create required directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)

    # Check if Varanasi cache exists, if not warn user
    cache_file = os.path.join('cache', 'varanasi_graph.pkl')
    if not os.path.exists(cache_file):
        print("=" * 70)
        print("WARNING: Varanasi map data not cached!")
        print("=" * 70)
        print("To speed up loading, run the preload script first:")
        print("  python preload_varanasi.py")
        print("\nThis will download the data once and cache it locally.")
        print("Subsequent loads will be instant!")
        print("=" * 70)
        print()

    print("=" * 70)
    print("A* Pathfinding Interactive Visualization")
    print("=" * 70)
    print("Starting Flask server with SocketIO support...")
    print("Open your browser and navigate to: http://localhost:5000")
    print("=" * 70)

    # Run with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
