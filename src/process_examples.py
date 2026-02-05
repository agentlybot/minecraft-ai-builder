#!/usr/bin/env python3
"""
Process Examples CLI

Command-line tool to process NBT files and extract style references.

Usage:
    # Process single NBT file
    python src/process_examples.py -i examples/style_references/medieval/german_estate.nbt -c medieval

    # Process all NBT files in a directory
    python src/process_examples.py -i examples/style_references/medieval/ -c medieval

    # Aggregate all examples in a category and update catalog
    python src/process_examples.py -i examples/style_references/medieval/ -c medieval --aggregate

    # List available categories
    python src/process_examples.py --list-categories
"""

import argparse
import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from style_reference import (
    StyleExtractor,
    StyleAggregator,
    PromptEnhancer,
    extract_style_from_nbt,
    aggregate_styles
)


def process_single_file(nbt_path: str, category: str, output_dir: str = None) -> bool:
    """
    Process a single NBT file.

    Args:
        nbt_path: Path to the NBT file
        category: Style category
        output_dir: Output directory for JSON (defaults to same as NBT)

    Returns:
        True if successful
    """
    print(f"\nProcessing: {nbt_path}")
    print(f"Category: {category}")

    # Determine output path
    if output_dir is None:
        output_dir = os.path.dirname(nbt_path)

    base_name = os.path.splitext(os.path.basename(nbt_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}.json")

    # Extract style reference
    ref = extract_style_from_nbt(nbt_path, category, output_path)

    if ref is None:
        print("  ERROR: Failed to extract style reference")
        return False

    # Print summary
    print(f"\n  Structure: {ref.name}")
    print(f"  Dimensions: {ref.metrics.proportions.width}x{ref.metrics.proportions.height}x{ref.metrics.proportions.depth}")
    print(f"  Block types: {ref.metrics.quality.block_variety}")
    print(f"  Detail score: {ref.metrics.quality.detail_score}/10")
    print(f"  Roof style: {ref.metrics.patterns.roof_style}")
    print(f"  Wall style: {ref.metrics.patterns.wall_style}")
    print(f"  Features: {', '.join(ref.metrics.patterns.features) or 'none detected'}")
    print(f"\n  Top materials:")
    for block, count in ref.metrics.top_blocks[:5]:
        print(f"    - {block}: {count}")

    print(f"\n  Output: {output_path}")
    return True


def process_directory(dir_path: str, category: str, aggregate: bool = False) -> bool:
    """
    Process all NBT files in a directory.

    Args:
        dir_path: Path to directory
        category: Style category
        aggregate: Whether to aggregate results and update catalog

    Returns:
        True if at least one file was processed
    """
    print(f"\nProcessing directory: {dir_path}")
    print(f"Category: {category}")

    extractor = StyleExtractor()
    references = extractor.extract_directory(dir_path, category)

    if not references:
        print("  No NBT files found or all failed to process")
        return False

    print(f"\n  Processed {len(references)} files")

    # Save individual JSON files
    for ref in references:
        output_path = os.path.join(dir_path, f"{ref.name}.json")
        ref.save_json(output_path)
        print(f"  Saved: {output_path}")

    if aggregate:
        print(f"\n  Aggregating {len(references)} examples...")

        # Aggregate styles
        agg = aggregate_styles(references, category)

        # Save aggregated style
        agg_path = os.path.join(dir_path, f"_{category}_aggregated.json")
        agg.save_json(agg_path)
        print(f"  Aggregated style saved: {agg_path}")

        # Update catalog
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        catalog_path = os.path.join(base_dir, 'examples', 'style_references', 'catalog.json')

        enhancer = PromptEnhancer(catalog_path)
        enhancer.add_style(category, agg)
        enhancer.save_catalog()
        print(f"  Catalog updated: {catalog_path}")

        # Print aggregated summary
        print(f"\n  === Aggregated Style: {category.upper()} ===")
        print(f"  Examples: {agg.example_count}")
        print(f"  Recommended walls: {', '.join(agg.recommended_walls)}")
        print(f"  Recommended roof: {', '.join(agg.recommended_roof)}")
        print(f"  Common roof style: {agg.common_roof_style}")
        print(f"  Common wall style: {agg.common_wall_style}")
        print(f"  Common features: {', '.join(agg.common_features)}")
        print(f"  Target block variety: {agg.target_block_variety}+")

    return True


def list_categories():
    """List available style categories."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    catalog_path = os.path.join(base_dir, 'examples', 'style_references', 'catalog.json')

    enhancer = PromptEnhancer(catalog_path)
    categories = enhancer.list_categories()

    if not categories:
        print("No style categories defined yet.")
        print("\nTo add a category, process NBT files with --aggregate:")
        print("  python src/process_examples.py -i path/to/nbt/files/ -c medieval --aggregate")
        return

    print("\nAvailable style categories:")
    for cat in categories:
        style = enhancer.catalog[cat]
        print(f"  - {cat}: {style.example_count} examples")


def main():
    parser = argparse.ArgumentParser(
        description='Process NBT files and extract style references',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single NBT file
  python src/process_examples.py -i medieval/german_estate.nbt -c medieval

  # Process all NBT files in a directory
  python src/process_examples.py -i medieval/ -c medieval

  # Aggregate and update catalog
  python src/process_examples.py -i medieval/ -c medieval --aggregate

  # List available categories
  python src/process_examples.py --list-categories
"""
    )

    parser.add_argument('-i', '--input', type=str,
                       help='Input NBT file or directory')
    parser.add_argument('-c', '--category', type=str, default='general',
                       help='Style category (e.g., medieval, modern, fantasy)')
    parser.add_argument('--aggregate', action='store_true',
                       help='Aggregate all examples in directory and update catalog')
    parser.add_argument('--list-categories', action='store_true',
                       help='List available style categories')

    args = parser.parse_args()

    if args.list_categories:
        list_categories()
        return

    if not args.input:
        parser.print_help()
        return

    input_path = args.input

    # Check if input exists
    if not os.path.exists(input_path):
        print(f"Error: Input path not found: {input_path}")
        sys.exit(1)

    if os.path.isfile(input_path):
        # Single file
        if not input_path.endswith('.nbt'):
            print(f"Error: Input file must be .nbt format: {input_path}")
            sys.exit(1)
        success = process_single_file(input_path, args.category)
    else:
        # Directory
        success = process_directory(input_path, args.category, args.aggregate)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
