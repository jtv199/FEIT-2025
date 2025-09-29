#!/usr/bin/env python3
import json
from collections import defaultdict

def find_all_depots():
    """Find all unique depots in the Victoria VMS dataset."""

    with open('extracted_data/2023_vms_victoria.json', 'r') as f:
        data = json.load(f)

    depots = defaultdict(list)

    for contract_key, contract in data.items():
        depot = contract.get('depot', {})

        if depot:
            depot_id = depot.get('id')
            depot_name = depot.get('name', 'Unknown')
            depot_short_code = depot.get('shortCode', '')

            # Get depot address if available
            depot_address = depot.get('address', {})
            depot_lat = depot_address.get('latitude')
            depot_lon = depot_address.get('longitude')
            depot_location = depot_address.get('name', '')

            depot_key = f"{depot_id}_{depot_name}"

            if depot_key not in [d['key'] for d in depots[depot_name]]:
                depots[depot_name].append({
                    'key': depot_key,
                    'id': depot_id,
                    'name': depot_name,
                    'short_code': depot_short_code,
                    'latitude': depot_lat,
                    'longitude': depot_lon,
                    'location_name': depot_location,
                    'contract_count': 0
                })

    # Count contracts per depot
    for contract_key, contract in data.items():
        depot = contract.get('depot', {})
        if depot:
            depot_name = depot.get('name', 'Unknown')
            depot_id = depot.get('id')
            depot_key = f"{depot_id}_{depot_name}"

            for depot_info in depots[depot_name]:
                if depot_info['key'] == depot_key:
                    depot_info['contract_count'] += 1
                    break

    return depots

def main():
    print("=== VICTORIA DEPOTS ANALYSIS ===\n")

    depots = find_all_depots()

    print(f"Found {len(depots)} unique depot names\n")

    print("=== DEPOT DETAILS ===")
    print(f"{'Depot Name':<20} {'ID':<5} {'Code':<8} {'Contracts':<10} {'Coordinates':<25} {'Location'}")
    print("-" * 100)

    total_contracts = 0

    for depot_name in sorted(depots.keys()):
        for depot_info in depots[depot_name]:
            contracts = depot_info['contract_count']
            total_contracts += contracts

            # Format coordinates
            if depot_info['latitude'] and depot_info['longitude']:
                coords = f"({depot_info['latitude']}, {depot_info['longitude']})"
                coords = coords[:24]
            else:
                coords = "No coordinates"

            location = depot_info['location_name'] or "Unknown"

            print(f"{depot_info['name']:<20} {depot_info['id']:<5} {depot_info['short_code']:<8} "
                  f"{contracts:<10} {coords:<25} {location}")

    print(f"\nTotal contracts across all depots: {total_contracts}")

    # Show depot summary
    print(f"\n=== DEPOT SUMMARY ===")
    depot_summary = []
    for depot_name in depots.keys():
        total_depot_contracts = sum(d['contract_count'] for d in depots[depot_name])
        depot_summary.append((depot_name, total_depot_contracts))

    depot_summary.sort(key=lambda x: x[1], reverse=True)

    for depot_name, contract_count in depot_summary:
        percentage = (contract_count / total_contracts * 100) if total_contracts > 0 else 0
        print(f"{depot_name:<20} {contract_count:>6} contracts ({percentage:.1f}%)")

    # Show depot coordinates for mapping
    print(f"\n=== DEPOT COORDINATES (for mapping) ===")
    for depot_name in sorted(depots.keys()):
        for depot_info in depots[depot_name]:
            if depot_info['latitude'] and depot_info['longitude']:
                print(f"{depot_info['name']}: {depot_info['latitude']}, {depot_info['longitude']}")

if __name__ == "__main__":
    main()