#!/usr/bin/env python3
"""
Main entry point for Tender Scraper Engine

Usage:
    python main.py --limit 10 --mode api
    python main.py --help
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config.settings import Settings
from database.connection import get_db
from pipeline.orchestrator import TenderPipeline
from utils.logger import setup_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Tender Scraper Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of tenders to scrape (default: all)'
    )
    
    parser.add_argument(
        '--mode',
        choices=['api', 'selenium', 'hybrid'],
        default='api',
        help='Scraping mode (default: api)'
    )
    
    parser.add_argument(
        '--visible',
        action='store_true',
        help='Show browser window (for selenium mode)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()


def main():
    """Main execution function."""
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logger(
        log_level='DEBUG' if args.verbose else 'INFO'
    )
    
    logger.info("="*80)
    logger.info("TENDER SCRAPER ENGINE - Starting")
    logger.info("="*80)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Limit: {args.limit or 'No limit'}")
    
    try:
        # Load settings
        settings = Settings()
        
        # Get database session
        db = next(get_db())
        
        # Initialize pipeline
        pipeline = TenderPipeline(
            db=db,
            mode=args.mode,
            headless=not args.visible
        )
        
        # Run pipeline
        pipeline.run_full_pipeline(limit=args.limit)
        
        logger.info("="*80)
        logger.info("COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("\nInterrupted by user")
        return 130
        
    except Exception as e:
        logger.error(f"FATAL ERROR: {e}", exc_info=True)
        return 1
    
    finally:
        # Cleanup
        if 'pipeline' in locals():
            pipeline.cleanup()


if __name__ == '__main__':
    sys.exit(main())

