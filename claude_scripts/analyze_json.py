#!/usr/bin/env python3
import json
import pandas as pd
from collections import defaultdict, Counter
from typing import Any, Dict, List, Tuple, Set

def explore_json_structure(data: Dict[str, Any], prefix: str = "", path: List[str] = None) -> List[Tuple[int, str, str, Any, int]]:
    """
    Recursively explore JSON structure and return field information.
    Returns: List of (field_number, field_path, field_type, sample_value, nesting_depth)
    """
    if path is None:
        path = []

    fields = []
    field_counter = 0

    def _explore(obj: Any, current_prefix: str = "", current_path: List[str] = None, depth: int = 0) -> None:
        nonlocal field_counter, fields

        if current_path is None:
            current_path = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                field_counter += 1
                new_path = current_path + [key]
                new_prefix = f"{current_prefix}.{key}" if current_prefix else key

                # Determine field type and complexity
                field_type = type(value).__name__
                if isinstance(value, dict):
                    field_type = f"dict({len(value)} keys)"
                elif isinstance(value, list):
                    field_type = f"list({len(value)} items)"

                fields.append((field_counter, new_prefix, field_type, value, depth))

                # Recurse into nested structures
                if isinstance(value, (dict, list)):
                    _explore(value, new_prefix, new_path, depth + 1)

        elif isinstance(obj, list) and obj:
            # Analyze first item in list to understand structure
            first_item = obj[0]
            if isinstance(first_item, dict):
                _explore(first_item, f"{current_prefix}[0]", current_path, depth + 1)

    _explore(data, prefix, path)
    return fields

def analyze_flattening_difficulty(fields: List[Tuple[int, str, str, Any, int]]) -> Dict[str, Any]:
    """Analyze which fields would be most difficult to flatten."""

    difficulty_scores = {}

    for field_num, field_path, field_type, sample_value, depth in fields:
        difficulty = 0
        reasons = []

        # Depth penalty
        difficulty += depth * 2
        if depth > 0:
            reasons.append(f"nested depth {depth}")

        # Type complexity penalty
        if "dict" in field_type:
            difficulty += 5
            reasons.append("dictionary object")
        elif "list" in field_type:
            difficulty += 3
            reasons.append("list/array")

        # Null handling
        if sample_value is None:
            difficulty += 1
            reasons.append("nullable field")

        # Variable structure detection
        if isinstance(sample_value, dict) and len(str(sample_value)) > 100:
            difficulty += 2
            reasons.append("complex nested structure")

        difficulty_scores[field_path] = {
            'difficulty': difficulty,
            'reasons': reasons,
            'type': field_type,
            'depth': depth,
            'field_number': field_num
        }

    return difficulty_scores

def main():
    print("=== JSON Structure Analysis ===\n")

    # Load the JSON file
    try:
        with open('data/out.json', 'r') as f:
            data = json.load(f)
        print(f"✓ Loaded JSON file with {len(data)} top-level contracts")
    except Exception as e:
        print(f"✗ Error loading JSON: {e}")
        return

    # Take first contract for structure analysis
    first_contract_key = list(data.keys())[0]
    first_contract = data[first_contract_key]

    print(f"✓ Analyzing structure using contract: {first_contract_key}\n")

    # Explore structure
    fields = explore_json_structure(first_contract)

    print(f"=== FIELD INVENTORY ({len(fields)} fields found) ===")
    print(f"{'#':<3} {'Field Path':<40} {'Type':<20} {'Depth':<5} {'Sample'}")
    print("-" * 100)

    for field_num, field_path, field_type, sample_value, depth in fields:
        # Truncate sample for display
        sample_str = str(sample_value)[:50]
        if len(str(sample_value)) > 50:
            sample_str += "..."

        print(f"{field_num:<3} {'  ' * depth}{field_path:<40} {field_type:<20} {depth:<5} {sample_str}")

    # Analyze flattening difficulty
    difficulty_analysis = analyze_flattening_difficulty(fields)

    print(f"\n=== FLATTENING DIFFICULTY ANALYSIS ===")

    # Sort by difficulty (most difficult first)
    sorted_fields = sorted(difficulty_analysis.items(), key=lambda x: x[1]['difficulty'], reverse=True)

    print(f"{'#':<3} {'Field Path':<40} {'Difficulty':<10} {'Reasons'}")
    print("-" * 100)

    for field_path, analysis in sorted_fields[:15]:  # Show top 15 most difficult
        field_num = analysis['field_number']
        difficulty = analysis['difficulty']
        reasons = ", ".join(analysis['reasons'])

        print(f"{field_num:<3} {field_path:<40} {difficulty:<10} {reasons}")

    # Summary statistics
    print(f"\n=== SUMMARY STATISTICS ===")

    total_fields = len(fields)
    nested_fields = len([f for f in fields if f[4] > 0])
    dict_fields = len([f for f in fields if "dict" in f[2]])
    list_fields = len([f for f in fields if "list" in f[2]])
    max_depth = max([f[4] for f in fields])

    print(f"Total fields: {total_fields}")
    print(f"Nested fields: {nested_fields} ({nested_fields/total_fields*100:.1f}%)")
    print(f"Dictionary fields: {dict_fields}")
    print(f"List/Array fields: {list_fields}")
    print(f"Maximum nesting depth: {max_depth}")

    # Flattening recommendations
    print(f"\n=== FLATTENING RECOMMENDATIONS ===")

    very_difficult = [f for f, a in difficulty_analysis.items() if a['difficulty'] > 7]
    moderate = [f for f, a in difficulty_analysis.items() if 3 < a['difficulty'] <= 7]
    easy = [f for f, a in difficulty_analysis.items() if a['difficulty'] <= 3]

    print(f"🔴 Very difficult to flatten ({len(very_difficult)} fields): Deep nesting, complex objects")
    print(f"🟡 Moderate difficulty ({len(moderate)} fields): Some nesting or special types")
    print(f"🟢 Easy to flatten ({len(easy)} fields): Simple types, minimal nesting")

    print(f"\nMost problematic fields for CSV flattening:")
    for field_path, analysis in sorted_fields[:5]:
        print(f"  - {field_path}: {', '.join(analysis['reasons'])}")

if __name__ == "__main__":
    main()