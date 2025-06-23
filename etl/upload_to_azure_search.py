#!/usr/bin/env python3
"""
Simple CLI for uploading experiences to Azure Search.
Migrated from backend to ETL directory for better organization.

USAGE EXAMPLES:
  # Create index and upload everything
  poetry run python upload_to_azure_search.py --index my-index --all --create-index
  
  # Upload only Reddit experiences with limit
  poetry run python upload_to_azure_search.py --index my-index --reddit --reddit-limit 100
  
  # Upload only studies 
  poetry run python upload_to_azure_search.py --index my-index --studies
  
  # Upload both with different limits
  poetry run python upload_to_azure_search.py --index my-index --all --reddit-limit 50 --studies-limit 25
  
  # Test what would be uploaded (dry run)
  poetry run python upload_to_azure_search.py --index my-index --all --dry-run
  
  # Upload studies from custom directory
  poetry run python upload_to_azure_search.py --index my-index --studies --studies-dir /path/to/studies

NOTES:
  - Reddit experiences come from TopicExperiences (Biohacking, Sleep, Pregnancy topics)
  - Studies come from JSON files in specified directory (default: nobsmed data directory)
  - Both data types go into the same Azure Search index with source_type differentiation
  - Embeddings are automatically generated for the health_disorder field
  - Only experiences meeting quality thresholds (action_score >= 2, outcomes_score >= 2) are uploaded
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Upload experiences to Azure Search")
    parser.add_argument("--index", required=True, help="Azure Search index name")
    parser.add_argument("--reddit", action="store_true", help="Upload Reddit experiences")
    parser.add_argument("--studies", action="store_true", help="Upload study experiences")
    parser.add_argument("--all", action="store_true", help="Upload both Reddit and studies")
    parser.add_argument("--reddit-limit", type=int, help="Limit Reddit experiences")
    parser.add_argument("--studies-limit", type=int, help="Limit study experiences") 
    parser.add_argument("--studies-dir", help="Studies directory path")
    parser.add_argument("--create-index", action="store_true", help="Create index first")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be uploaded")

    args = parser.parse_args()

    # Ensure at least one upload type is specified
    if not any([args.reddit, args.studies, args.all]):
        print("❌ Must specify --reddit, --studies, or --all")
        sys.exit(1)

    try:
        # Import here to avoid loading dependencies for help/validation
        sys.path.append(str(Path(__file__).parent.parent / "backend"))
        from etl.azure_search_indexing.search_add_experiences import (
            ExperienceV0, upload_experiences, upload_studies, upload_all_experiences
        )

        if args.dry_run:
            print("🔍 DRY RUN - Would perform:")
            if args.create_index:
                print(f"  - Create index: {args.index}")
            if args.reddit or args.all:
                print(f"  - Upload Reddit experiences (limit: {args.reddit_limit or 'none'})")
            if args.studies or args.all:
                print(f"  - Upload studies (limit: {args.studies_limit or 'none'})")
            return

        # Create index if requested
        if args.create_index:
            print(f"🏗️  Creating index: {args.index}")
            ExperienceV0.create_index(index_name=args.index)

        # Upload based on options
        if args.all:
            print("📊 Uploading all experiences (Reddit + Studies)")
            upload_all_experiences(
                index_name=args.index,
                reddit_limit=args.reddit_limit,
                studies_limit=args.studies_limit,
                studies_dir=args.studies_dir
            )
        else:
            if args.reddit:
                print("🔗 Uploading Reddit experiences")
                upload_experiences(index_name=args.index, limit=args.reddit_limit)
            
            if args.studies:
                print("📚 Uploading study experiences")
                upload_studies(
                    index_name=args.index,
                    limit=args.studies_limit,
                    studies_dir=args.studies_dir
                )

        print("✅ Upload completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()