#!/usr/bin/env python3
import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

def euclidean_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Euclidean distance between two points in kilometers."""
    lat_diff = (lat2 - lat1) * 111  # ~111 km per degree latitude
    lon_diff = (lon2 - lon1) * 85   # ~85 km per degree longitude in Victoria
    return math.sqrt(lat_diff**2 + lon_diff**2)

def find_multiple_equipment_options(date_range_allowance: int = 10) -> Dict:
    """
    Find contracts that have multiple VMS equipment options available
    from recently completed contracts instead of depot.
    """

    with open('extracted_data/2023_vms_victoria.json', 'r') as f:
        data = json.load(f)

    # Get depot location
    depot_lat, depot_lon = -37.6805, 145.0064

    contracts_list = []

    # Prepare contract data
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

    # Find contracts with multiple equipment options
    multiple_options = {}

    for i, current_contract in enumerate(contracts_list):
        current_start = current_contract['start_date']
        current_lat = current_contract['latitude']
        current_lon = current_contract['longitude']
        current_depot_distance = current_contract['distance_to_depot']

        # Find all available equipment options for this contract
        available_options = []

        for j, previous_contract in enumerate(contracts_list):
            if i == j:
                continue

            prev_end = previous_contract['end_date']
            days_difference = (current_start - prev_end).days

            # Check if previous contract ended within allowable range
            if 0 <= days_difference <= date_range_allowance:
                prev_lat = previous_contract['latitude']
                prev_lon = previous_contract['longitude']

                site_to_site_distance = euclidean_distance(
                    prev_lat, prev_lon, current_lat, current_lon
                )

                # Check if site-to-site is closer than depot-to-site
                if site_to_site_distance < current_depot_distance:
                    potential_savings = current_depot_distance - site_to_site_distance

                    available_options.append({
                        'previous_contract': previous_contract['contract_key'],
                        'previous_site': previous_contract['site_name'],
                        'previous_end': prev_end.strftime('%Y-%m-%d'),
                        'days_gap': days_difference,
                        'site_to_site_km': round(site_to_site_distance, 1),
                        'potential_savings_km': round(potential_savings, 1),
                        'savings_percentage': round((potential_savings / current_depot_distance) * 100, 1)
                    })

        # Only include contracts with multiple options (2 or more)
        if len(available_options) >= 2:
            # Sort options by potential savings
            available_options.sort(key=lambda x: x['potential_savings_km'], reverse=True)

            multiple_options[current_contract['contract_key']] = {
                'current_contract': current_contract['contract_key'],
                'current_site': current_contract['site_name'],
                'current_start': current_start.strftime('%Y-%m-%d'),
                'depot_distance_km': round(current_depot_distance, 1),
                'num_options': len(available_options),
                'options': available_options
            }

    return multiple_options

def main():
    print("=== MULTIPLE VMS EQUIPMENT OPTIONS ANALYSIS ===\n")

    multiple_options = find_multiple_equipment_options()

    print(f"Found {len(multiple_options)} contracts with multiple equipment options\n")

    if multiple_options:
        # Sort by number of options
        sorted_contracts = sorted(multiple_options.items(),
                                key=lambda x: x[1]['num_options'], reverse=True)

        print("=== CONTRACTS WITH MOST OPTIONS ===")
        print(f"{'Contract':<12} {'Site':<25} {'Start Date':<12} {'Options':<8} {'Best Savings'}")
        print("-" * 80)

        for contract_key, data in sorted_contracts[:15]:
            best_savings = data['options'][0]['potential_savings_km']
            print(f"{contract_key:<12} {data['current_site'][:24]:<25} {data['current_start']:<12} "
                  f"{data['num_options']:<8} {best_savings} km")

        # Show detailed example
        print(f"\n=== DETAILED EXAMPLE: {sorted_contracts[0][0]} ===")
        example = sorted_contracts[0][1]

        print(f"Contract: {example['current_contract']}")
        print(f"Site: {example['current_site']}")
        print(f"Start Date: {example['current_start']}")
        print(f"Depot Distance: {example['depot_distance_km']} km")
        print(f"Available Options: {example['num_options']}")
        print()

        print("Equipment Options:")
        print(f"{'Rank':<5} {'From Contract':<12} {'Days Gap':<9} {'Distance':<10} {'Savings':<8} {'%'}")
        print("-" * 60)

        for i, option in enumerate(example['options'][:10], 1):
            print(f"{i:<5} {option['previous_contract']:<12} {option['days_gap']} days    "
                  f"{option['site_to_site_km']:<10} {option['potential_savings_km']:<8} "
                  f"{option['savings_percentage']}%")

        # Summary statistics
        print(f"\n=== SUMMARY STATISTICS ===")
        total_contracts_with_options = len(multiple_options)
        total_options = sum(data['num_options'] for data in multiple_options.values())
        avg_options = total_options / total_contracts_with_options if total_contracts_with_options > 0 else 0

        max_options = max(data['num_options'] for data in multiple_options.values())

        print(f"Contracts with multiple options: {total_contracts_with_options}")
        print(f"Total equipment options available: {total_options}")
        print(f"Average options per contract: {avg_options:.1f}")
        print(f"Maximum options for single contract: {max_options}")

        # Distribution of option counts
        option_counts = defaultdict(int)
        for data in multiple_options.values():
            option_counts[data['num_options']] += 1

        print(f"\nOption Count Distribution:")
        for count in sorted(option_counts.keys()):
            contracts = option_counts[count]
            print(f"  {count} options: {contracts} contracts")

    else:
        print("No contracts found with multiple equipment options.")

if __name__ == "__main__":
    main()