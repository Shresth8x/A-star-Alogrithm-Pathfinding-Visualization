"""
Main script for A* pathfinding visualization on Chicago and Rome street networks.
"""

import time
from typing import List, Tuple

from src.map_data import MapDataManager, CityMap, print_map_stats
from src.routes import get_chicago_routes, get_rome_routes, RouteCollection, print_all_routes, Route
from src.astar import astar_with_tracking, AStarResult
from src.visualizer import create_and_save_visualization


def run_pathfinding(city_map: CityMap, route: Route) -> Tuple[AStarResult, float]:
    """
    Run A* pathfinding for a route and measure execution time.

    Args:
        city_map: City map data
        route: Route to find path for

    Returns:
        Tuple of (result, execution_time_seconds)
    """
    print(f"\n{'='*70}")
    print(f"Running A* for: {route.name}")
    print(f"Description: {route.description}")
    print(f"Start node: {route.start_node}")
    print(f"End node: {route.end_node}")
    print(f"{'='*70}")

    start_time = time.time()
    result = astar_with_tracking(city_map.graph, route.start_node, route.end_node)
    execution_time = time.time() - start_time

    if result.success:
        print(f"[SUCCESS] Path found!")
        print(f"  Path length: {result.path_length:.2f} meters")
        print(f"  Nodes in path: {len(result.path)}")
        print(f"  Nodes explored: {result.nodes_explored}")
        print(f"  Execution time: {execution_time:.4f} seconds")
        print(f"  Exploration frames: {len(result.exploration_history)}")
    else:
        print(f"[FAILED] No path found")
        print(f"  Nodes explored: {result.nodes_explored}")
        print(f"  Execution time: {execution_time:.4f} seconds")

    return result, execution_time


def process_city(city_name: str, city_map: CityMap, routes: RouteCollection,
                manager: MapDataManager):
    """
    Process all routes for a city.

    Args:
        city_name: Name of the city
        city_map: City map data
        routes: Collection of routes for the city
        manager: Map data manager
    """
    print(f"\n{'#'*70}")
    print(f"# Processing {city_name}")
    print(f"{'#'*70}")

    # Print map statistics
    print_map_stats(city_map)

    # Resolve route coordinates to actual nodes
    print(f"\nResolving route coordinates to graph nodes...")
    routes.resolve_nodes(city_map, manager)

    # Print route information
    print_all_routes(routes, city_map, manager)

    # Process each route
    total_time = 0
    successful_routes = 0

    for i, route in enumerate(routes.routes, 1):
        print(f"\n[{i}/{len(routes.routes)}]", end=" ")

        # Run pathfinding
        result, exec_time = run_pathfinding(city_map, route)
        total_time += exec_time

        if result.success:
            successful_routes += 1

            # Create visualization
            print(f"Creating visualization...")
            viz_start = time.time()
            output_path = create_and_save_visualization(city_map, route, result)
            viz_time = time.time() - viz_start
            print(f"Visualization saved to: {output_path}")
            print(f"Visualization time: {viz_time:.2f} seconds")

        print(f"{'-'*70}")

    # Print summary
    print(f"\n{'='*70}")
    print(f"{city_name} Summary:")
    print(f"  Routes processed: {len(routes.routes)}")
    print(f"  Successful paths: {successful_routes}")
    print(f"  Total pathfinding time: {total_time:.4f} seconds")
    print(f"  Average time per route: {total_time/len(routes.routes):.4f} seconds")
    print(f"{'='*70}\n")


def main():
    """Main execution function."""
    print("="*70)
    print("A* Pathfinding Visualization")
    print("Cities: Chicago & Rome")
    print("Data Source: OpenStreetMap via OSMnx")
    print("="*70)

    # Initialize map data manager
    manager = MapDataManager(cache_dir="cache")

    # Get route collections
    chicago_routes = get_chicago_routes()
    rome_routes = get_rome_routes()

    print(f"\nTotal routes to process:")
    print(f"  Chicago: {len(chicago_routes.routes)}")
    print(f"  Rome: {len(rome_routes.routes)}")
    print(f"  Total: {len(chicago_routes.routes) + len(rome_routes.routes)}")

    # Process Chicago
    print("\n" + "="*70)
    print("PHASE 1: Loading Chicago Map Data")
    print("="*70)
    chicago_map = manager.get_chicago_downtown(use_cache=True)
    process_city("Chicago", chicago_map, chicago_routes, manager)

    # Process Rome
    print("\n" + "="*70)
    print("PHASE 2: Loading Rome Map Data")
    print("="*70)
    rome_map = manager.get_rome_downtown(use_cache=True)
    process_city("Rome", rome_map, rome_routes, manager)

    # Final summary
    print("\n" + "="*70)
    print("ALL PROCESSING COMPLETE")
    print("="*70)
    print(f"Visualizations saved in the 'output' directory")
    print(f"Map data cached in the 'cache' directory")
    print("\nTo view animations:")
    print("  - Open .gif files in any image viewer")
    print("  - Animations show the A* algorithm exploration in real-time")
    print("="*70)


if __name__ == "__main__":
    main()
