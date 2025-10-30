#!/usr/bin/env python3
"""
Success Rate Verification Script

This script tests the API scraper and measures its success rate.
Target: 90%+ success rate for tender extraction.

Usage:
    python scripts/verify_success_rate.py --runs 10 --limit 100
    python scripts/verify_success_rate.py --verbose
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers.api_scraper import APIScraper
from src.utils.logger import setup_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Verify API Scraper Success Rate',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--runs',
        type=int,
        default=5,
        help='Number of test runs to perform (default: 5)'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Number of tenders to scrape per run (default: 10)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser.parse_args()


def run_single_test(scraper, limit):
    """
    Run a single scraping test.
    
    Args:
        scraper: APIScraper instance
        limit: Number of tenders to scrape
        
    Returns:
        Tuple of (success, count, error_message)
    """
    try:
        tenders = scraper.scrape_tender_list(limit=limit)
        
        if not tenders:
            return (False, 0, "No tenders returned")
        
        # Validate tender data quality
        valid_tenders = 0
        for tender in tenders:
            # Check that tender has required fields
            if tender.get('tender_id') and tender.get('work_name'):
                valid_tenders += 1
        
        success_rate = (valid_tenders / len(tenders) * 100) if tenders else 0
        
        if valid_tenders == 0:
            return (False, len(tenders), "No valid tenders found")
        
        return (True, valid_tenders, None)
        
    except Exception as e:
        return (False, 0, str(e))


def calculate_statistics(results):
    """
    Calculate success statistics.
    
    Args:
        results: List of (success, count, error) tuples
        
    Returns:
        Dictionary with statistics
    """
    total_runs = len(results)
    successful_runs = sum(1 for success, _, _ in results if success)
    total_tenders = sum(count for _, count, _ in results)
    
    success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0
    avg_tenders = total_tenders / total_runs if total_runs > 0 else 0
    
    # Collect unique errors
    errors = {}
    for success, _, error in results:
        if not success and error:
            errors[error] = errors.get(error, 0) + 1
    
    return {
        'total_runs': total_runs,
        'successful_runs': successful_runs,
        'failed_runs': total_runs - successful_runs,
        'success_rate': success_rate,
        'total_tenders': total_tenders,
        'avg_tenders_per_run': avg_tenders,
        'errors': errors
    }


def print_report(stats, target_rate=90.0):
    """
    Print verification report.
    
    Args:
        stats: Statistics dictionary
        target_rate: Target success rate percentage
    """
    print("\n" + "=" * 80)
    print("SUCCESS RATE VERIFICATION REPORT")
    print("=" * 80)
    print(f"Total Runs:            {stats['total_runs']}")
    print(f"Successful Runs:       {stats['successful_runs']}")
    print(f"Failed Runs:           {stats['failed_runs']}")
    print(f"Success Rate:          {stats['success_rate']:.1f}%")
    print(f"Total Tenders Scraped: {stats['total_tenders']}")
    print(f"Avg Tenders per Run:   {stats['avg_tenders_per_run']:.1f}")
    print("-" * 80)
    
    # Print status
    if stats['success_rate'] >= target_rate:
        print(f"✅ PASSED: Success rate {stats['success_rate']:.1f}% meets target {target_rate}%")
    else:
        print(f"❌ FAILED: Success rate {stats['success_rate']:.1f}% below target {target_rate}%")
    
    # Print errors if any
    if stats['errors']:
        print("\nErrors encountered:")
        for error, count in stats['errors'].items():
            print(f"  - {error} ({count} times)")
    
    print("=" * 80 + "\n")
    
    return stats['success_rate'] >= target_rate


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logger(
        log_level='DEBUG' if args.verbose else 'INFO'
    )
    
    logger.info("=" * 80)
    logger.info("API SCRAPER SUCCESS RATE VERIFICATION")
    logger.info("=" * 80)
    logger.info(f"Test Runs: {args.runs}")
    logger.info(f"Tenders per Run: {args.limit}")
    logger.info(f"Target Success Rate: 90%")
    logger.info("")
    
    try:
        # Initialize scraper
        logger.info("Initializing API scraper...")
        scraper = APIScraper()
        logger.info("Scraper initialized successfully")
        logger.info("")
        
        # Run tests
        results = []
        for i in range(args.runs):
            logger.info(f"Run {i+1}/{args.runs}...")
            success, count, error = run_single_test(scraper, args.limit)
            results.append((success, count, error))
            
            if success:
                logger.info(f"  ✅ Success: {count} tenders extracted")
            else:
                logger.warning(f"  ❌ Failed: {error}")
            logger.info("")
        
        # Calculate and print statistics
        stats = calculate_statistics(results)
        passed = print_report(stats)
        
        # Cleanup
        scraper.cleanup()
        
        return 0 if passed else 1
        
    except KeyboardInterrupt:
        logger.warning("\nInterrupted by user")
        return 130
        
    except Exception as e:
        logger.error(f"FATAL ERROR: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
