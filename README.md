# A* Pathfinding Visualization

An interactive web application and static GIF generator for visualizing the A* pathfinding algorithm on real street networks using OpenStreetMap data.

![Chicago_Loop_Diagonal](https://github.com/user-attachments/assets/6e083d11-762a-46e4-8085-042d7051a840)

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Interactive Web Application

Start the web server:

```bash
python app.py
```

Open your browser to `http://localhost:5000`

### Static GIF Generation

Generate animated visualizations for predefined routes:

```bash
python main.py
```

Outputs are saved in the `output/` directory.

## Features

### Interactive Web Application

- Real-time pathfinding visualization with live algorithm exploration
- Interactive map interface powered by Leaflet.js
- Multiple coordinate input formats:
  - DMS format: `16°17'02.6"N 80°27'15.1"E`
  - Decimal with direction: `41.8781N 87.6298W`
  - Comma-separated: `41.8781, -87.6298`
  - Click directly on the map
- Playback controls: Play, Pause, Reset with adjustable speed (0.5x to 5x)
- Works worldwide: Load maps from any location on Earth
- Real-time statistics: Track nodes explored, frontier size, path length

### Static GIF Generation

- Animated GIF visualization for predefined routes
- Multiple routes for Chicago and Rome
- Visual comparison between grid-like vs irregular street layouts

## Examples

### Chicago Grid System
![Chicago_West_Loop_to_East_Loop](https://github.com/user-attachments/assets/b8927e02-3ed5-4384-b072-d2ae188809e2)

The grid pattern in Chicago allows for direct routes with minimal exploration.

### Rome Irregular Streets

![Rome_Forum_Diagonal](https://github.com/user-attachments/assets/2356bf4a-2714-430d-bb6a-3e3aa2bdfcbc)

The irregular medieval streets in Rome require more exploration to find optimal paths.

## How to Use

### Web Application

1. **Enter Coordinates**:
   - Choose "Text Input" and enter start/end coordinates
   - OR choose "Click on Map" and click to set start and end points
   - Use "Quick Examples" buttons for pre-configured routes

2. **Load Map**:
   - Click "Load Map" to download street network data from OpenStreetMap
   - Map data is cached locally for faster subsequent loads

3. **Run Pathfinding**:
   - Click "Play" to start the A* algorithm visualization
   - Adjust speed with the slider (0.5x - 5x)
   - Use "Pause" to stop and "Reset" to clear visualization

4. **Observe**:
   - Watch the algorithm explore nodes in real-time
   - See frontier (orange), evaluated nodes (blue), and current node (red)
   - Final path shown in bold red when complete

### GIF Generation

The `main.py` script will:
1. Download street network data for downtown Chicago and Rome (cached locally)
2. Run A* pathfinding for 8 predefined routes (4 per city)
3. Generate animated GIF visualizations showing the algorithm's exploration process
4. Display statistics (nodes explored, path length, execution time)

## Visualization Color Coding

- Gray: Unexplored streets
- Orange: Nodes in open set (being considered)
- Blue: Nodes in closed set (already evaluated)
- Red/Bold: Final shortest path
- Green: Start point
- Red: Goal point

## Project Structure

```
pathFinder/
├── app.py                 # Flask web server
├── main.py                # Static GIF generator script
├── requirements.txt       # Python dependencies
├── src/                   # Core algorithm modules
│   ├── astar.py           # A* algorithm implementation
│   ├── astar_streaming.py # Generator-based A* for real-time visualization
│   ├── map_data.py        # OpenStreetMap data manager
│   ├── coordinate_parser.py # DMS coordinate format parser
│   ├── routes.py          # Predefined routes for Chicago and Rome
│   └── visualizer.py      # Animated visualization engine
├── templates/             # Web interface templates
│   └── index.html
├── static/                # Static web assets
│   ├── js/
│   │   └── app.js
│   └── css/
│       └── style.css
├── assets/                # README visualizations
└── cache/                 # Cached map data (auto-generated, git-ignored)
```

## How A* Works

The A* algorithm finds the shortest path by using:
- g(n): Actual cost from start to node n
- h(n): Heuristic estimate to goal (haversine distance)
- f(n) = g(n) + h(n): Total estimated cost

The algorithm explores nodes with the lowest f(n) first, guaranteeing an optimal path.

## Coordinate Format Examples

The web application supports multiple coordinate formats:

**DMS (Degrees Minutes Seconds):**
```
16°17'02.6"N 80°27'15.1"E
41°52'41.2"N 87°37'47.3"W
```

**Decimal with Direction:**
```
16.284056N 80.454194E
41.8781N 87.6298W
```

**Decimal (Comma-separated):**
```
16.284056, 80.454194
41.8781, -87.6298
```

## Technical Details

**Algorithm:**
- A* (A-Star): Informed search algorithm using f(n) = g(n) + h(n)
- Heuristic: Haversine distance (great circle distance on Earth)
- Graph: Undirected multi-graph from OSMnx
- Edge weights: Actual street lengths in meters

**Web Technology Stack:**
- Backend: Flask + Flask-SocketIO + Eventlet
- Frontend: Vanilla JavaScript + Leaflet.js + Socket.IO
- Data: OpenStreetMap via OSMnx library
- Caching: Local pickle cache for map data

## Troubleshooting

**Port Already in Use**
If port 5000 is already in use, modify `app.py` to use a different port.

**Slow Map Loading**
- First load for a new area takes longer (downloading from OpenStreetMap)
- Subsequent loads are instant (uses cached data)
- Very large route spans (>5km) are automatically capped

**No Path Found**
- Ensure start and end points are on drivable streets
- Some areas may have disconnected road networks
- Try points closer together or in more connected areas

**Browser Compatibility**
- Tested on Chrome, Firefox, Edge, Safari
- Requires JavaScript enabled
- WebSocket support required (all modern browsers)

## Data Source

Street network data is sourced from OpenStreetMap using the OSMnx library. Data is automatically downloaded on first run and cached locally for subsequent runs.
