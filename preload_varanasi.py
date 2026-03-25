"""
Preload script to download and cache Varanasi city map data.
Run this script once to download and cache the data locally for faster loading.
"""

from src.map_data import MapDataManager
import os

def main():
    """Preload Varanasi city map data to cache."""
    print("=" * 70)
    print("Varanasi Map Data Preloader")
    print("=" * 70)
    print("\nThis script will download Varanasi city street network data")
    print("from OpenStreetMap and save it to the local cache.")
    print("\nThis is a one-time download - subsequent loads will be instant!")
    print("=" * 70)

    # Clear Hyderabad cache if it exists
    hyderabad_cache = os.path.join('cache', 'hyderabad_graph.pkl')
    if os.path.exists(hyderabad_cache):
        try:
            os.remove(hyderabad_cache)
            print("\nCleared Hyderabad cache file.")
        except Exception as e:
            print(f"\nWarning: Could not delete Hyderabad cache: {e}")

    # Initialize map data manager
    manager = MapDataManager(cache_dir="cache")

    # Download and cache Varanasi data
    # This will download if not cached, or load from cache if it exists
    print("\nLoading Varanasi city map...")
    print("(This may take several minutes on first run)")

    try:
        city_map = manager.get_varanasi_city(use_cache=True)

        print("\n" + "=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print(f"\nVaranasi map data cached successfully!")
        print(f"\nMap Statistics:")
        print(f"  Nodes (intersections): {city_map.graph.number_of_nodes()}")
        print(f"  Edges (streets): {city_map.graph.number_of_edges()}")
        print(f"  Bounding box: N={city_map.bbox[0]:.4f}, S={city_map.bbox[1]:.4f}, "
              f"E={city_map.bbox[2]:.4f}, W={city_map.bbox[3]:.4f}")
        print(f"\nCache location: cache/varanasi_graph.pkl")
        print("\nThe map will now load instantly from cache!")
        print("=" * 70)

    except Exception as e:
        print("\n" + "=" * 70)
        print("ERROR!")
        print("=" * 70)
        print(f"\nFailed to download Varanasi map data: {e}")
        print("\nPlease check your internet connection and try again.")
        print("=" * 70)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
