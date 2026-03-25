# A* Pathfinding Interactive Visualization - Usage Guide

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the web server**:
   ```bash
   python app.py
   ```

3. **Open in browser**:
   Navigate to `http://localhost:5000`

## Detailed Usage

### 1. Entering Coordinates

You have two options for specifying start and end points:

#### Option A: Text Input (Default)

Enter coordinates in one of these formats:

**DMS Format** (Most Precise):
```
Start: 16°17'02.6"N 80°27'15.1"E
End: 16°17'30.0"N 80°27'45.0"E
```

**Decimal with Direction**:
```
Start: 41.8781N 87.6298W
End: 41.8820N 87.6210W
```

**Comma-separated Decimal**:
```
Start: 41.8781, -87.6298
End: 41.8820, -87.6210
```

**Tips**:
- Use the example buttons for quick pre-configured routes
- Press Enter in input fields to load map quickly
- Coordinates are validated before loading

#### Option B: Click on Map

1. Select "Click on Map" radio button
2. Click anywhere on the map to set START point (green marker appears)
3. Click again to set END point (red marker appears)
4. Map loads automatically after second click

**Tips**:
- Zoom into your desired area first for precision
- Can switch back to text input anytime
- Useful for exploring unfamiliar areas

### 2. Loading the Map

After entering coordinates, click **"Load Map"**:

**What happens**:
- Coordinates are validated
- System calculates optimal map area to download
- Street network downloaded from OpenStreetMap (cached for reuse)
- Map renders with street network in gray
- Start (green) and end (red) markers placed at nearest road intersections

**Loading time**:
- First load of new area: 2-10 seconds
- Cached areas: < 1 second
- Progress shown in status bar

**Map Information Panel**:
- Displays number of nodes (intersections) and edges (streets)
- Shows actual start/end node IDs used by algorithm
- Confirms map is ready for pathfinding

### 3. Running the Algorithm

Once map is loaded, use **Playback Controls**:

#### Play Button
- Starts A* algorithm execution
- Algorithm steps streamed in real-time
- Watch the exploration unfold on the map

#### Pause Button
- Temporarily stops visualization
- Resume from same point with Play
- Useful for examining specific steps

#### Reset Button
- Clears all visualization layers
- Keeps map loaded
- Ready to run algorithm again

#### Speed Slider
- Adjust visualization speed from 0.5x (slower) to 5x (faster)
- Default: 1.0x (100ms per step)
- Change speed even while running
- Faster speeds good for large graphs

### 4. Understanding the Visualization

#### Color Coding

**Streets**:
- Gray lines: Road network (all drivable streets)

**Algorithm State**:
- **Blue dots**: Closed set (already evaluated nodes)
- **Orange dots**: Open set (frontier - nodes being considered)
- **Red star**: Current node being evaluated
- **Light red line**: Partial path being explored
- **Bold red line**: Final shortest path (when found)

**Markers**:
- **Green circle**: Start point
- **Red circle**: Goal/destination point

#### Statistics Panel

Real-time metrics during execution:

- **Status**: Current algorithm state (Running/Paused/Path Found)
- **Nodes Explored**: Total nodes evaluated (closed set size)
- **Frontier Size**: Nodes in open set
- **Current g(n)**: Actual distance from start to current node
- **Current f(n)**: Estimated total cost (g + heuristic)
- **Path Length**: Final path distance (shown when complete)

#### What to Observe

1. **Heuristic Guidance**: Algorithm explores toward goal, not randomly
2. **Frontier Expansion**: Orange nodes spread from start toward goal
3. **Efficiency**: Minimal exploration in optimal cases
4. **Path Reconstruction**: Red line traces optimal route when found

### 5. Quick Examples

Three pre-configured routes for testing:

#### Chicago Loop
- Grid street pattern
- Fast pathfinding (direct routes)
- Good for seeing algorithm efficiency

#### Rome Forum
- Irregular medieval streets
- More exploration needed
- Shows A* handling complex layouts

#### Custom India Route
- Example of DMS coordinate format
- Demonstrates international support

Click any example button to auto-fill coordinates.

## Advanced Features

### Coordinate System Details

**Supported Formats**:

1. **DMS** (Degrees, Minutes, Seconds):
   - Format: `DD°MM'SS.S"X DDD°MM'SS.S"X`
   - Example: `16°17'02.6"N 80°27'15.1"E`
   - Most precise format
   - X = N/S for latitude, E/W for longitude

2. **Decimal with Direction**:
   - Format: `DD.DDDDDDX DDD.DDDDDDX`
   - Example: `16.284056N 80.454194E`
   - Compact format

3. **Decimal Signed**:
   - Format: `DD.DDDDDD, DDD.DDDDDD`
   - Example: `16.284056, 80.454194`
   - Positive = N/E, Negative = S/W
   - Standard GPS format

4. **Space-separated DMS**:
   - Format: `DD MM SS.S X DDD MM SS.S X`
   - Example: `16 17 02.6 N 80 27 15.1 E`
   - Alternative DMS format

### Map Area Calculation

The system automatically determines map area:

1. Calculates midpoint between start and end
2. Measures distance between points
3. Sets radius = distance × 0.75 (with 50% margin)
4. Minimum radius: 300m
5. Maximum radius: 5km (for performance)

This ensures both points are always included in the downloaded network.

### Caching System

**How it works**:
- Maps cached by center point and radius
- Cache stored in `cache/` directory as pickle files
- Automatic cache lookup before download
- Instant loading for previously visited areas

**Cache management**:
- Persistent across application restarts
- Can safely delete `cache/` folder to clear
- Each cached map ~100KB-1MB depending on size

## Tips for Best Results

### Choosing Good Routes

**Do**:
- Start and end on major roads
- Keep distance reasonable (100m - 5km)
- Choose points in same connected network
- Explore different street patterns (grids vs. irregular)

**Avoid**:
- Very close points (< 50m apart)
- Disconnected areas (islands, gated communities)
- Non-drivable areas (parks, buildings)
- Extremely long distances (> 5km)

### Optimal Visualization

**Speed Settings**:
- 0.5x - 1.0x: Good for learning, detailed observation
- 1.0x - 2.0x: Normal viewing speed
- 2.0x - 5.0x: Large graphs, time-saving

**Map Interaction**:
- Zoom in during visualization for detail
- Pan to follow algorithm exploration
- Use pause to examine specific states

### Performance Considerations

**Factors affecting speed**:
- Number of nodes (more nodes = longer visualization)
- Network complexity (grids faster than irregular)
- Chosen visualization speed
- Browser/hardware performance

**Typical performance**:
- Small area (50-100 nodes): 5-10 seconds @ 1.0x
- Medium area (100-200 nodes): 10-30 seconds @ 1.0x
- Large area (200+ nodes): 30-60+ seconds @ 1.0x

## Common Use Cases

### 1. Education
- Demonstrate A* algorithm concepts
- Compare with other algorithms (Dijkstra, BFS)
- Show heuristic guidance effects
- Visualize real-world pathfinding

### 2. Urban Planning
- Analyze street network connectivity
- Find shortest routes between locations
- Study traffic flow patterns
- Compare different city layouts

### 3. Algorithm Research
- Test A* performance on real networks
- Compare different heuristics
- Analyze exploration patterns
- Benchmark against other algorithms

### 4. General Interest
- Explore cities worldwide
- Find routes in your neighborhood
- Compare grid vs. organic street patterns
- Learn about graph algorithms interactively

## Troubleshooting

### Map Won't Load
**Symptoms**: Error message after clicking Load Map

**Possible causes**:
1. Invalid coordinates (outside valid range)
2. No road network at location (ocean, remote areas)
3. Network connectivity issues
4. OpenStreetMap API temporarily unavailable

**Solutions**:
- Verify coordinates are in valid range (lat: -90 to 90, lon: -180 to 180)
- Choose location with roads
- Check internet connection
- Try again after a moment

### No Path Found
**Symptoms**: "No Path Found" message after running algorithm

**Possible causes**:
1. Start and end in disconnected road networks
2. One-way street restrictions
3. Isolated road segments

**Solutions**:
- Choose points closer together
- Select points on major roads
- Try different locations in same area

### Slow Performance
**Symptoms**: Visualization takes very long

**Possible causes**:
1. Very large map area
2. Complex street network
3. Slow browser/hardware

**Solutions**:
- Increase visualization speed (slider to 3x-5x)
- Choose smaller area (closer points)
- Use modern browser
- Close other applications

### Connection Lost
**Symptoms**: "Connection lost" toast notification

**Possible causes**:
1. Server stopped/crashed
2. Network interruption
3. Browser page reload needed

**Solutions**:
- Refresh browser page
- Restart server (python app.py)
- Check network connection

## Keyboard Shortcuts

Currently, the application uses mouse interaction. Future versions may include:
- Space: Play/Pause toggle
- R: Reset visualization
- +/-: Adjust speed
- Arrow keys: Step through algorithm frames

## Browser Developer Tools

For debugging or learning:

1. **Open Console** (F12):
   - View WebSocket messages
   - See algorithm state updates
   - Check for errors

2. **Network Tab**:
   - Monitor map loading
   - Check API calls
   - View WebSocket frames

3. **Performance Tab**:
   - Profile rendering
   - Identify bottlenecks

## API Documentation

For developers integrating with the backend:

### REST Endpoints

**Parse Coordinates**:
```
POST /api/parse-coordinates
Body: {"start": "...", "end": "..."}
Response: {"success": true, "start": {...}, "end": {...}}
```

**Load Map**:
```
POST /api/load-map
Body: {"start_lat": 16.28, "start_lon": 80.45, ...}
Response: {"success": true, "map_info": {...}, "edges": [...]}
```

### WebSocket Events

**Client to Server**:
- `start_pathfinding`: Begin algorithm with speed
- `pause_pathfinding`: Pause visualization
- `resume_pathfinding`: Resume from pause
- `reset_pathfinding`: Clear visualization
- `set_speed`: Change visualization speed

**Server to Client**:
- `algorithm_step`: Each algorithm state update
- `paused`: Confirmation of pause
- `reset`: Confirmation of reset
- `error`: Error messages
- `connected`: Initial connection confirmation

## Next Steps

After mastering the basics:

1. **Try Different Cities**: Explore various urban layouts worldwide
2. **Compare Patterns**: Grid cities (US) vs. organic (Europe) vs. planned (Asia)
3. **Experiment with Speed**: Find optimal viewing speed for learning
4. **Study the Code**: Examine algorithm implementation in source files
5. **Extend Features**: Add custom heuristics, additional algorithms, or metrics

## Support

For issues or questions:
- Check this guide first
- Review README.md for technical details
- Examine source code comments
- Test with provided examples

Happy pathfinding!
