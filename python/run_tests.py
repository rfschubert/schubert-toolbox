#!/usr/bin/env python3
"""
Test runner for Schubert Toolbox Python implementation.

This script runs all unit tests and provides a summary of results.
"""

import unittest
import sys
import os
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def run_all_tests():
    """Run all unit tests."""
    # Discover and run tests
    test_dir = Path(__file__).parent / "tests"
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Log summary
    logger.info("=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")

    if result.failures:
        logger.error("FAILURES:")
        for test, traceback in result.failures:
            logger.error(f"- {test}: {traceback}")

    if result.errors:
        logger.error("ERRORS:")
        for test, traceback in result.errors:
            logger.error(f"- {test}: {traceback}")
    
    # Return success status
    return len(result.failures) == 0 and len(result.errors) == 0

def run_specific_test(test_module):
    """Run a specific test module."""
    try:
        suite = unittest.TestLoader().loadTestsFromName(test_module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return len(result.failures) == 0 and len(result.errors) == 0
    except Exception as e:
        logger.error(f"Error running test {test_module}: {e}")
        return False

def run_test_category(category):
    """Run tests from a specific category (unit, integration, bdd)."""
    test_dir = Path(__file__).parent / "tests" / category
    if not test_dir.exists():
        logger.error(f"Test category '{category}' not found")
        return False

    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern='test_*.py')

    logger.info(f"Running {category.upper()} tests...")
    logger.info("=" * 40)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    logger.info(f"{category.upper()} TESTS SUMMARY:")
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")

    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        # Check if it's a test category
        if arg in ['unit', 'integration', 'bdd']:
            success = run_test_category(arg)
        else:
            # Run specific test
            success = run_specific_test(arg)
    else:
        # Run all tests
        success = run_all_tests()

    sys.exit(0 if success else 1)
