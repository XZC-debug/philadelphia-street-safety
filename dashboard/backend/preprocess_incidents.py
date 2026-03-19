"""
Preprocess incidents data and assign to neighborhoods based on spatial location
This script performs spatial join between incidents and neighborhood boundaries
"""

import geopandas as gpd
import pandas as pd
import json
import os
from config import Config

def create_neighborhood_boundaries():
    """Create neighborhood boundaries from street data and area data"""
    print("[INFO] Creating neighborhood boundaries...")

    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(backend_dir))

    boundaries = {}

    # Load UNIVERSITY_CITY from area file (most reliable)
    try:
        uc_area = gpd.read_file(os.path.join(project_root, "area", "UNIVERSITY_CITY_a.shp"))
        boundaries['UNIVERSITY_CITY'] = uc_area.iloc[0].geometry
        print("[OK] Loaded UNIVERSITY_CITY boundary from area file")
    except Exception as e:
        print(f"[WARN] Failed to load UNIVERSITY_CITY area: {e}")

    # Create boundaries for other neighborhoods using street data convex hull
    street_files = {
        'Center City': os.path.join(project_root, "street", "Center City.shp"),
        'KENSINGTON': os.path.join(project_root, "street", "KENSINGTON.shp"),
        'POINT_BREEZE': os.path.join(project_root, "street", "POINT_BREEZE.shp"),
    }

    for neighborhood, filepath in street_files.items():
        if os.path.exists(filepath):
            try:
                streets = gpd.read_file(filepath)
                # Convert to WGS84 if needed
                if streets.crs != 'EPSG:4326':
                    streets = streets.to_crs('EPSG:4326')

                # Create boundary as convex hull with buffer
                boundary = streets.geometry.unary_union.convex_hull
                # Add small buffer to ensure points on edges are included
                boundary = boundary.buffer(0.0001)
                boundaries[neighborhood] = boundary
                print(f"[OK] Created {neighborhood} boundary from street data (convex hull with buffer)")
            except Exception as e:
                print(f"[WARN] Failed to load {neighborhood} streets: {e}")
        else:
            print(f"[WARN] Street file not found: {filepath}")

    return boundaries


def assign_incidents_to_neighborhoods(boundaries):
    """Spatially join incidents to neighborhoods"""
    print("\n[INFO] Loading incidents data...")

    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(backend_dir))

    # Load incidents
    incidents_file = os.path.join(project_root, "incidents", "incidents_part1_part2.shp")
    incidents = gpd.read_file(incidents_file)

    print(f"[OK] Loaded {len(incidents)} incident records")
    print(f"     Incidents CRS: {incidents.crs}")

    # Create GeoDataFrame for neighborhoods
    neighborhoods_gdf = gpd.GeoDataFrame(
        {
            'neighborhood': list(boundaries.keys()),
            'geometry': list(boundaries.values())
        },
        crs='EPSG:4326'
    )

    # Perform spatial join
    print("\n[INFO] Performing spatial join (this may take a while)...")
    joined = gpd.sjoin(
        incidents,
        neighborhoods_gdf,
        how='left',
        predicate='within'
    )

    # Count incidents per neighborhood
    incident_counts = joined['neighborhood'].value_counts().to_dict()

    print("\n[INFO] Incident counts by neighborhood:")
    for neighborhood in Config.NEIGHBORHOODS:
        count = incident_counts.get(neighborhood, 0)
        print(f"  {neighborhood}: {count}")

    # Also get incident types per neighborhood
    incident_types_by_neighborhood = {}
    for neighborhood in Config.NEIGHBORHOODS:
        neighborhood_incidents = joined[joined['neighborhood'] == neighborhood]
        if len(neighborhood_incidents) > 0:
            # Count by text_gener (general incident type)
            counts = neighborhood_incidents['text_gener'].value_counts().head(10).to_dict()
            incident_types_by_neighborhood[neighborhood] = counts
        else:
            incident_types_by_neighborhood[neighborhood] = {}

    return incident_counts, incident_types_by_neighborhood


def save_incident_statistics(incident_counts, incident_types):
    """Save incident statistics to JSON file"""
    backend_dir = os.path.dirname(os.path.abspath(__file__))

    stats_data = {
        'incident_counts': incident_counts,
        'incident_types': incident_types,
        'generated_at': pd.Timestamp.now().isoformat()
    }

    output_file = os.path.join(backend_dir, "processed_data", "incidents_stats.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(stats_data, f, indent=2)

    print(f"\n[OK] Saved incident statistics to {output_file}")
    return output_file


if __name__ == "__main__":
    print("=" * 60)
    print("Philadelphia Street Safety - Incidents Spatial Analysis")
    print("=" * 60)

    # Step 1: Create neighborhood boundaries
    boundaries = create_neighborhood_boundaries()

    if not boundaries:
        print("[ERROR] Failed to create any neighborhood boundaries!")
        exit(1)

    # Step 2: Assign incidents to neighborhoods
    incident_counts, incident_types = assign_incidents_to_neighborhoods(boundaries)

    # Step 3: Save results
    save_incident_statistics(incident_counts, incident_types)

    print("\n" + "=" * 60)
    print("[SUCCESS] Incident spatial analysis completed!")
    print("=" * 60)
