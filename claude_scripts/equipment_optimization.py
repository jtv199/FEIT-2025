#!/usr/bin/env python3
import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

def is_in_victoria(latitude: float, longitude: float) -> bool:
    """
    Check if coordinates are within Victoria, Australia boundaries.
    Victoria approximate boundaries:
    - Latitude: -34.0 to -39.2
    - Longitude: 140.9 to 150.0
    """
    return (-39.2 <= latitude <= -34.0) and (140.9 <= longitude <= 150.0)

def euclidean_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Euclidean distance between two points in kilometers."""
    # Convert to approximate km (rough conversion for Victoria)
    lat_diff = (lat2 - lat1) * 111  # ~111 km per degree latitude
    lon_diff = (lon2 - lon1) * 85   # ~85 km per degree longitude in Victoria
    return math.sqrt(lat_diff**2 + lon_diff**2)

def filter_victoria_vms_contracts():
    """Filter 2023 VMS contracts for Victoria with valid coordinates."""

    with open('extracted_data/2023_vms.json', 'r') as f:
        data = json.load(f)

    victoria_contracts = {}

    for contract_key, contract in data.items():
        site_address = contract.get('siteAddress')

        if not site_address:
            continue

        latitude = site_address.get('latitude')
        longitude = site_address.get('longitude')

        if latitude is None or longitude is None:
            continue

        try:
            lat = float(latitude)
            lon = float(longitude)

            if is_in_victoria(lat, lon):
                victoria_contracts[contract_key] = contract

        except (ValueError, TypeError):
            continue

    # Save filtered contracts
    with open('extracted_data/2023_vms_victoria.json', 'w') as f:
        json.dump(victoria_contracts, f, indent=2)

    return len(victoria_contracts)

def find_depot_location():
    """Find depot coordinates from the contract data."""

    with open('extracted_data/2023_vms_victoria.json', 'r') as f:
        data = json.load(f)

    # Look for depot coordinates in the depot.address field
    for contract_key, contract in data.items():
        depot = contract.get('depot', {})
        if depot and 'address' in depot:
            address = depot['address']
            lat = address.get('latitude')
            lon = address.get('longitude')

            if lat and lon:
                try:
                    depot_lat = float(lat)
                    depot_lon = float(lon)
                    depot_name = depot.get('name', 'Unknown')

                    print(f"Found depot: {depot_name}")
                    print(f"Coordinates: ({depot_lat}, {depot_lon})")

                    return depot_lat, depot_lon, depot_name
                except (ValueError, TypeError):
                    continue

    # Fallback to approximate Melbourne depot location
    print("Using fallback Melbourne depot location")
    return -37.6805, 145.0064, "Melbourne Depot"

def equipment_site_to_site_optimization(
    date_range_allowance: int = 10,
    max_distance_from_depot: float = 100
) -> List[Dict]:
    """
    Find opportunities to move equipment site-to-site instead of depot-to-site.

    Args:
        date_range_allowance: Days equipment can stay on site after off-hire
        max_distance_from_depot: Maximum distance to consider for optimization

    Returns:
        List of optimization opportunities
    """

    with open('extracted_data/2023_vms_victoria.json', 'r') as f:
        data = json.load(f)

    # Get depot location
    depot_lat, depot_lon, depot_name = find_depot_location()

    opportunities = []
    contracts_list = []

    # Prepare contract data with dates and coordinates
    for contract_key, contract in data.items():
        site_address = contract.get('siteAddress', {})
        lat = site_address.get('latitude')
        lon = site_address.get('longitude')

        start_date_str = contract.get('startDate')
        end_date_str = contract.get('actualEndDate') or contract.get('plannedEndDate')

        if not all([lat, lon, start_date_str, end_date_str]):
            continue

        try:
            site_lat = float(lat)
            site_lon = float(lon)
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))

            # Calculate distance to depot
            distance_to_depot = euclidean_distance(site_lat, site_lon, depot_lat, depot_lon)

            contracts_list.append({
                'contract_key': contract_key,
                'site_name': site_address.get('name', ''),
                'latitude': site_lat,
                'longitude': site_lon,
                'start_date': start_date,
                'end_date': end_date,
                'distance_to_depot': distance_to_depot
            })

        except (ValueError, TypeError):
            continue

    # Sort contracts by start date
    contracts_list.sort(key=lambda x: x['start_date'])

    # Find optimization opportunities
    for i, current_contract in enumerate(contracts_list):
        current_start = current_contract['start_date']
        current_lat = current_contract['latitude']
        current_lon = current_contract['longitude']
        current_depot_distance = current_contract['distance_to_depot']

        # Look for recently ended contracts within date range
        for j, previous_contract in enumerate(contracts_list):
            if i == j:
                continue

            prev_end = previous_contract['end_date']
            days_difference = (current_start - prev_end).days

            # Check if previous contract ended within allowable range
            if 0 <= days_difference <= date_range_allowance:
                prev_lat = previous_contract['latitude']
                prev_lon = previous_contract['longitude']

                # Calculate distance between sites
                site_to_site_distance = euclidean_distance(
                    prev_lat, prev_lon, current_lat, current_lon
                )

                # Check if site-to-site is closer than depot-to-site
                if site_to_site_distance < current_depot_distance:
                    potential_savings = current_depot_distance - site_to_site_distance

                    opportunities.append({
                        'current_contract': current_contract['contract_key'],
                        'current_site': current_contract['site_name'],
                        'current_start': current_start.strftime('%Y-%m-%d'),
                        'previous_contract': previous_contract['contract_key'],
                        'previous_site': previous_contract['site_name'],
                        'previous_end': prev_end.strftime('%Y-%m-%d'),
                        'days_gap': days_difference,
                        'site_to_site_km': round(site_to_site_distance, 1),
                        'depot_to_site_km': round(current_depot_distance, 1),
                        'potential_savings_km': round(potential_savings, 1),
                        'savings_percentage': round((potential_savings / current_depot_distance) * 100, 1)
                    })

    return opportunities

def main():
    print("=== EQUIPMENT SITE-TO-SITE OPTIMIZATION ===\n")

    # Step 1: Filter Victoria contracts
    print("1. Filtering Victoria VMS contracts with coordinates...")
    victoria_count = filter_victoria_vms_contracts()
    print(f"   Found {victoria_count} VMS contracts in Victoria with coordinates\n")

    # Step 2: Find optimization opportunities
    print("2. Analyzing site-to-site optimization opportunities...")
    opportunities = equipment_site_to_site_optimization()

    print(f"   Found {len(opportunities)} optimization opportunities\n")

    # Step 3: Display results
    if opportunities:
        print("=== TOP OPTIMIZATION OPPORTUNITIES ===")
        print(f"{'Current Contract':<12} {'Previous Contract':<12} {'Gap':<4} {'Site-Site':<10} {'Depot-Site':<10} {'Savings':<8} {'%':<5}")
        print("-" * 70)

        # Sort by potential savings
        opportunities.sort(key=lambda x: x['potential_savings_km'], reverse=True)

        for opp in opportunities[:15]:  # Show top 15
            print(f"{opp['current_contract']:<12} {opp['previous_contract']:<12} {opp['days_gap']}d   "
                  f"{opp['site_to_site_km']:<10} {opp['depot_to_site_km']:<10} "
                  f"{opp['potential_savings_km']:<8} {opp['savings_percentage']:<5}%")

        total_savings = sum(opp['potential_savings_km'] for opp in opportunities)
        print(f"\nTotal potential savings: {total_savings:.1f} km")
        print(f"Average savings per opportunity: {total_savings/len(opportunities):.1f} km")
    else:
        print("No optimization opportunities found with current parameters.")

if __name__ == "__main__":
    main()