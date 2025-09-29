#!/usr/bin/env python3
import json

def extract_chain_coordinates():
    """Extract coordinates for the longest chains for mapping."""

    with open('extracted_data/2023_vms_victoria_with_chains.json', 'r') as f:
        data = json.load(f)

    # Define the chains
    chains = {
        'length_8': ['HC7894', 'HC7956', 'HC8061', 'HC8214', 'HC8329', 'HC8470', 'HC8033', 'HC8702'],
        'length_4_gippsland': ['HC7847', 'HC7854', 'HC7939', 'HC8685'],
        'length_4_northern': ['HC9386', 'HC9500', 'HC9540', 'HC9830'],
        'length_4_inner': ['HC12945', 'HC12899', 'HC13339', 'HC13417'],
        'length_4_eastern': ['HC13002', 'HC13160', 'HC13612', 'HC9908']
    }

    mapping_data = {}

    for chain_name, contract_list in chains.items():
        chain_data = []

        for i, contract_key in enumerate(contract_list):
            if contract_key in data:
                contract = data[contract_key]
                site_address = contract.get('siteAddress', {})

                lat = site_address.get('latitude')
                lon = site_address.get('longitude')

                if lat and lon:
                    try:
                        lat_float = float(lat)
                        lon_float = float(lon)

                        chain_data.append({
                            'contract': contract_key,
                            'order': i + 1,
                            'latitude': lat_float,
                            'longitude': lon_float,
                            'site_name': site_address.get('name', ''),
                            'start_date': contract.get('startDate', ''),
                            'savings_km': contract.get('next_contract', {}).get('savings_km', 0) if contract.get('next_contract') else 0
                        })
                    except (ValueError, TypeError):
                        continue

        mapping_data[chain_name] = chain_data

    # Save mapping data as JSON for visualization tools
    with open('reports/chain_mapping_data.json', 'w') as f:
        json.dump(mapping_data, f, indent=2)

    # Create CSV for easy import to mapping tools
    with open('reports/chain_mapping_data.csv', 'w') as f:
        f.write('chain_name,contract,order,latitude,longitude,site_name,start_date,savings_km\n')

        for chain_name, chain_data in mapping_data.items():
            for point in chain_data:
                f.write(f"{chain_name},{point['contract']},{point['order']},"
                       f"{point['latitude']},{point['longitude']},"
                       f'"{point["site_name"]}",{point["start_date"]},{point["savings_km"]}\n')

    # Print summary for verification
    print("=== CHAIN MAPPING DATA EXTRACTED ===\n")

    for chain_name, chain_data in mapping_data.items():
        print(f"{chain_name.replace('_', ' ').title()}:")
        print(f"  Points: {len(chain_data)}")

        if chain_data:
            # Calculate bounding box
            lats = [p['latitude'] for p in chain_data]
            lons = [p['longitude'] for p in chain_data]

            print(f"  Latitude range: {min(lats):.4f} to {max(lats):.4f}")
            print(f"  Longitude range: {min(lons):.4f} to {max(lons):.4f}")

            # Show first and last points
            first = chain_data[0]
            last = chain_data[-1]
            print(f"  Route: {first['site_name']} → {last['site_name']}")

        print()

    print("Files created:")
    print("- reports/chain_mapping_data.json (for web mapping)")
    print("- reports/chain_mapping_data.csv (for GIS tools)")

    # Create simple HTML map example
    create_simple_map_html(mapping_data)

def create_simple_map_html(mapping_data):
    """Create a simple HTML file with Leaflet map showing the chains."""

    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>VMS Equipment Chain Optimization</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <style>
        #map { height: 600px; }
        body { font-family: Arial, sans-serif; margin: 20px; }
        .chain-info { margin-bottom: 10px; }
        .legend { background: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 15px rgba(0,0,0,0.2); }
    </style>
</head>
<body>
    <h1>VMS Equipment Chain Optimization - Victoria 2023</h1>

    <div class="chain-info">
        <strong>Legend:</strong>
        <span style="color: red;">●</span> Length 8 Chain (Bendigo) |
        <span style="color: blue;">●</span> Length 4 Gippsland |
        <span style="color: green;">●</span> Length 4 Northern |
        <span style="color: orange;">●</span> Length 4 Inner |
        <span style="color: purple;">●</span> Length 4 Eastern
    </div>

    <div id="map"></div>

    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script>
        // Initialize map centered on Victoria
        var map = L.map('map').setView([-37.4713, 144.7852], 8);

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Define colors for each chain
        var chainColors = {
            'length_8': 'red',
            'length_4_gippsland': 'blue',
            'length_4_northern': 'green',
            'length_4_inner': 'orange',
            'length_4_eastern': 'purple'
        };

        // Chain data
        var chainData = """ + json.dumps(mapping_data, indent=8) + """;

        // Add chains to map
        Object.keys(chainData).forEach(function(chainName) {
            var chain = chainData[chainName];
            var color = chainColors[chainName];

            if (chain.length > 0) {
                // Create polyline for chain
                var coords = chain.map(function(point) {
                    return [point.latitude, point.longitude];
                });

                var polyline = L.polyline(coords, {
                    color: color,
                    weight: 3,
                    opacity: 0.7
                }).addTo(map);

                // Add markers for each point
                chain.forEach(function(point, index) {
                    var marker = L.circleMarker([point.latitude, point.longitude], {
                        color: 'white',
                        fillColor: color,
                        fillOpacity: 0.8,
                        radius: 6,
                        weight: 2
                    }).addTo(map);

                    // Add popup with details
                    marker.bindPopup(
                        '<strong>' + point.contract + '</strong><br>' +
                        'Order: ' + point.order + '<br>' +
                        'Site: ' + point.site_name + '<br>' +
                        'Date: ' + point.start_date.substring(0, 10) + '<br>' +
                        'Savings: ' + point.savings_km + ' km'
                    );
                });
            }
        });

        // Add depot marker
        var depot = L.marker([-37.6805, 145.0064], {
            icon: L.icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-black.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            })
        }).addTo(map);

        depot.bindPopup('<strong>VIC ELECTRONICS DEPOT</strong><br>Main depot for equipment');

    </script>
</body>
</html>"""

    with open('reports/chain_map_visualization.html', 'w') as f:
        f.write(html_content)

    print("- reports/chain_map_visualization.html (interactive map)")

if __name__ == "__main__":
    extract_chain_coordinates()