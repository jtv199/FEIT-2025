#!/usr/bin/env python3
import json

def analyze_vms_coordinates():
    """Analyze latitude and longitude data completeness in 2023 VMS contracts."""

    with open('extracted_data/2023_vms.json', 'r') as f:
        data = json.load(f)

    coord_stats = {
        'has_both_coords': 0,
        'has_lat_only': 0,
        'has_lng_only': 0,
        'has_neither': 0,
        'no_site_address': 0,
        'samples_with_coords': [],
        'samples_without_coords': []
    }

    for contract_key, contract in data.items():
        site_address = contract.get('siteAddress')

        if not site_address:
            coord_stats['no_site_address'] += 1
            continue

        latitude = site_address.get('latitude')
        longitude = site_address.get('longitude')

        # Check for null, empty string, or missing values
        has_lat = latitude is not None and latitude != ''
        has_lng = longitude is not None and longitude != ''

        if has_lat and has_lng:
            coord_stats['has_both_coords'] += 1
            if len(coord_stats['samples_with_coords']) < 10:
                coord_stats['samples_with_coords'].append({
                    'contract': contract_key,
                    'name': site_address.get('name', ''),
                    'latitude': latitude,
                    'longitude': longitude
                })
        elif has_lat and not has_lng:
            coord_stats['has_lat_only'] += 1
        elif not has_lat and has_lng:
            coord_stats['has_lng_only'] += 1
        else:
            coord_stats['has_neither'] += 1
            if len(coord_stats['samples_without_coords']) < 10:
                coord_stats['samples_without_coords'].append({
                    'contract': contract_key,
                    'name': site_address.get('name', ''),
                    'latitude': latitude,
                    'longitude': longitude
                })

    return coord_stats

def main():
    print("=== VMS CONTRACTS COORDINATE ANALYSIS (2023) ===\n")

    stats = analyze_vms_coordinates()

    total_contracts = 2791
    has_both = stats['has_both_coords']
    has_lat_only = stats['has_lat_only']
    has_lng_only = stats['has_lng_only']
    has_neither = stats['has_neither']
    no_site_address = stats['no_site_address']

    print(f"=== COORDINATE STATISTICS (VMS CONTRACTS) ===")
    print(f"Total VMS contracts: {total_contracts}")
    print(f"Has both lat/lng: {has_both} ({has_both/total_contracts*100:.1f}%)")
    print(f"Has latitude only: {has_lat_only} ({has_lat_only/total_contracts*100:.1f}%)")
    print(f"Has longitude only: {has_lng_only} ({has_lng_only/total_contracts*100:.1f}%)")
    print(f"Has neither coordinate: {has_neither} ({has_neither/total_contracts*100:.1f}%)")
    print(f"No site address: {no_site_address} ({no_site_address/total_contracts*100:.1f}%)")

    print(f"\n=== SUMMARY ===")
    null_coords = has_neither + no_site_address
    print(f"Total contracts with NULL coordinates: {null_coords} ({null_coords/total_contracts*100:.1f}%)")
    print(f"Total contracts with valid coordinates: {has_both} ({has_both/total_contracts*100:.1f}%)")

    # Show samples with coordinates
    print(f"\n=== SAMPLE VMS LOCATIONS WITH COORDINATES ===")
    for sample in stats['samples_with_coords']:
        print(f"{sample['contract']}: {sample['name']} - ({sample['latitude']}, {sample['longitude']})")

    # Show samples without coordinates
    print(f"\n=== SAMPLE VMS LOCATIONS WITHOUT COORDINATES ===")
    for sample in stats['samples_without_coords']:
        lat_str = str(sample['latitude']) if sample['latitude'] is not None else 'None'
        lng_str = str(sample['longitude']) if sample['longitude'] is not None else 'None'
        print(f"{sample['contract']}: {sample['name']} - (lat: {lat_str}, lng: {lng_str})")

if __name__ == "__main__":
    main()