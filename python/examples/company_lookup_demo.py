#!/usr/bin/env python3
"""
Company Lookup Demonstration

This example demonstrates the CompanyManager functionality for Brazilian
company (CNPJ) data lookup using the BrasilAPI driver.

Features demonstrated:
- Basic company lookup
- First-to-respond pattern
- Error handling
- Data validation
- Performance comparison
"""

import sys
import os
import time
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from managers.company_manager import CompanyManager
from standards.core.base import ValidationError


def main():
    """Demonstrate CompanyManager functionality."""
    print("Company Lookup Demonstration")
    print("=" * 60)

    manager = CompanyManager()
    test_cnpj = "11.222.333/0001-81"  # Example CNPJ

    print(f"Available drivers: {manager.list_drivers()}")
    print(f"Testing CNPJ: {test_cnpj}")
    print()

    # Example 1: Basic company lookup
    print("Example 1: Basic Company Lookup")
    print("-" * 40)

    try:
        company = manager.get(test_cnpj)

        print(f"Success!")
        print(f"   Company: {company.get_display_name()}")
        print(f"   CNPJ: {company.cnpj}")
        print(f"   Legal Name: {company.legal_name}")
        print(f"   Trade Name: {company.trade_name or 'N/A'}")
        print(f"   Status: {company.status}")
        print(f"   Active: {company.is_active()}")
        print(f"   Source: {company.verification_source}")

        if company.primary_activity:
            print(f"   Activity: {company.primary_activity}")

        if company.phone:
            print(f"   Phone: {company.phone}")

        if company.email:
            print(f"   Email: {company.email}")

        if company.address:
            print(f"   Address: {company.get_full_address()}")

    except Exception as e:
        print(f"Error: {e}")

    print()

    # Example 2: First-to-respond pattern
    print("Example 2: First-to-Respond Pattern")
    print("-" * 40)
    
    start_time = time.time()
    try:
        company = manager.get_first_response_sync(test_cnpj)
        elapsed = time.time() - start_time

        print(f"Success!")
        print(f"   Response time: {elapsed:.3f} seconds")
        print(f"   Fastest driver: {company.verification_source}")
        print(f"   Company: {company.get_display_name()}")

    except Exception as e:
        print(f"Error: {e}")

    print()

    # Example 3: Async usage
    print("Example 3: Async Usage")
    print("-" * 40)

    async def async_demo():
        """Demonstrate async usage."""
        try:
            start_time = time.time()
            company = await manager.get_first_response(test_cnpj)
            elapsed = time.time() - start_time

            print(f"Async success!")
            print(f"   Response time: {elapsed:.3f} seconds")
            print(f"   Driver: {company.verification_source}")
            print(f"   Company: {company.get_display_name()}")

        except Exception as e:
            print(f"Async error: {e}")

    # Run async example
    try:
        asyncio.run(async_demo())
    except Exception as e:
        print(f"Async example skipped: {e}")

    print()

    # Example 4: Error handling
    print("Example 4: Error Handling")
    print("-" * 40)
    
    invalid_cnpjs = [
        "00.000.000/0001-00",  # Invalid CNPJ
        "invalid-cnpj",        # Invalid format
        "123",                 # Too short
    ]
    
    for invalid_cnpj in invalid_cnpjs:
        try:
            company = manager.get_first_response_sync(invalid_cnpj, timeout=3.0)
            print(f"Unexpected success for {invalid_cnpj}: {company.get_display_name()}")
        except ValidationError as e:
            print(f"Expected validation error for {invalid_cnpj}: {e}")
        except Exception as e:
            print(f"Expected error for {invalid_cnpj}: {type(e).__name__}")

    print()

    # Example 5: Data validation
    print("Example 5: Data Validation")
    print("-" * 40)
    
    def validate_company_data(company):
        """Validate essential company data."""
        issues = []
        
        if not company.cnpj:
            issues.append("Missing CNPJ")
        
        if not company.legal_name:
            issues.append("Missing legal name")
        
        if not company.is_active():
            issues.append(f"Company not active: {company.status}")
        
        return issues
    
    try:
        company = manager.get_first_response_sync(test_cnpj)
        issues = validate_company_data(company)
        
        if issues:
            print(f"Validation issues:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print(f"Company data validation passed!")
            print(f"   Company: {company.get_display_name()}")
            print(f"   Status: {company.status}")
            print(f"   Active: {company.is_active()}")

    except Exception as e:
        print(f"Validation error: {e}")

    print()
    print("Demonstration completed!")
    print("=" * 60)
    print()
    print("Key Features Demonstrated:")
    print("   • Basic company data lookup")
    print("   • First-to-respond pattern for performance")
    print("   • Async and sync APIs")
    print("   • Comprehensive error handling")
    print("   • Data validation patterns")
    print("   • Automatic CNPJ formatting")
    print("   • Address resolution (when available)")


if __name__ == "__main__":
    main()
