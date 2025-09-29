#!/usr/bin/env python3
import json
from datetime import datetime

def analyze_length4_chains():
    """Analyze the 4 chains of length 4 in detail."""

    with open('extracted_data/2023_vms_victoria_with_chains.json', 'r') as f:
        data = json.load(f)

    # The 4 chains of length 4 from previous analysis
    length4_chains = [
        ['HC7847', 'HC7854', 'HC7939', 'HC8685'],
        ['HC9386', 'HC9500', 'HC9540', 'HC9830'],
        ['HC12945', 'HC12899', 'HC13339', 'HC13417'],
        ['HC13002', 'HC13160', 'HC13612', 'HC9908']
    ]

    print("=== LENGTH 4 CHAINS ANALYSIS ===\n")

    for i, chain in enumerate(length4_chains, 1):
        print(f"Chain {i}: {' → '.join(chain)}")

        chain_details = []
        total_savings = 0

        for contract_key in chain:
            if contract_key in data:
                contract = data[contract_key]
                site_address = contract.get('siteAddress', {})

                site_name = site_address.get('name', 'Unknown')
                town = site_address.get('town', '')
                line1 = site_address.get('line1', '')

                # Build location description
                location = site_name
                if town and town not in site_name:
                    location += f", {town}"

                start_date = contract.get('startDate', '')
                if start_date:
                    try:
                        date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime('%b %d')
                    except:
                        formatted_date = start_date[:10]
                else:
                    formatted_date = 'Unknown'

                # Get savings from next contract link
                next_contract = contract.get('next_contract')
                savings = next_contract.get('savings_km', 0) if next_contract else 0
                total_savings += savings

                chain_details.append({
                    'contract': contract_key,
                    'location': location[:40],
                    'date': formatted_date,
                    'savings': savings
                })

        # Print chain details
        for j, detail in enumerate(chain_details):
            if j < len(chain_details) - 1:
                print(f"  {detail['contract']} ({detail['date']}) - {detail['location']}")
                if detail['savings'] > 0:
                    print(f"    ↓ saves {detail['savings']} km")
            else:
                print(f"  {detail['contract']} ({detail['date']}) - {detail['location']}")

        print(f"  Total savings: {total_savings:.1f} km")

        # Generate explanation
        if len(chain_details) >= 2:
            start_date = chain_details[0]['date']
            end_date = chain_details[-1]['date']
            locations = [detail['location'].split(',')[0] for detail in chain_details]

            # Try to identify common areas/patterns
            explanation = generate_chain_explanation(chain_details, total_savings)
            print(f"  Explanation: {explanation}")

        print()

def generate_chain_explanation(chain_details, total_savings):
    """Generate a sentence explanation for the chain."""

    if len(chain_details) < 2:
        return "Single contract chain."

    start_date = chain_details[0]['date']
    end_date = chain_details[-1]['date']

    # Extract location names (first part before comma)
    locations = []
    for detail in chain_details:
        location = detail['location'].split(',')[0].strip()
        # Clean up common prefixes
        location = location.replace('Job ', '').replace('Head Office', 'Office')
        locations.append(location)

    # Check for geographic patterns
    melbourne_suburbs = ['Frankston', 'Dandenong', 'Moorabbin', 'Mordialloc', 'Dromana', 'Mornington']
    regional_areas = ['Bendigo', 'Ballarat', 'Geelong', 'Shepparton', 'Warrnambool']
    highways = ['Calder', 'Princes', 'Hume', 'Western']

    # Identify pattern
    if any(suburb in ' '.join(locations) for suburb in melbourne_suburbs):
        area_type = "Melbourne metropolitan"
    elif any(area in ' '.join(locations) for area in regional_areas):
        area_type = "regional Victoria"
    elif any(hwy in ' '.join(locations) for hwy in highways):
        area_type = "highway corridor"
    else:
        area_type = "Victoria"

    # Build explanation
    duration_days = (datetime.strptime(end_date + " 2023", '%b %d %Y') -
                    datetime.strptime(start_date + " 2023", '%b %d %Y')).days

    if duration_days < 0:  # Year rollover
        duration_days += 365

    explanation = (f"Equipment flows through {area_type} over {duration_days} days "
                  f"({start_date} to {end_date}), saving {total_savings:.0f}km total by "
                  f"moving between {locations[0]} → {locations[-1]} via intermediate sites.")

    return explanation

if __name__ == "__main__":
    analyze_length4_chains()