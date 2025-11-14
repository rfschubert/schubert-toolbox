#!/usr/bin/env python3
"""
Linting script for Schubert Toolbox.

This script provides easy access to all linting and code quality tools.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🔍 {description}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Main linting function."""
    parser = argparse.ArgumentParser(description="Run linting tools on Schubert Toolbox")
    parser.add_argument("--check", action="store_true", help="Check only, don't fix")
    parser.add_argument("--fix", action="store_true", help="Fix issues automatically")
    parser.add_argument("--all", action="store_true", help="Run all checks")
    parser.add_argument("--ruff", action="store_true", help="Run ruff linter")
    parser.add_argument("--mypy", action="store_true", help="Run mypy type checker")
    parser.add_argument("--security", action="store_true", help="Run security checks")
    parser.add_argument("--unused", action="store_true", help="Check for unused imports")
    parser.add_argument("path", nargs="?", default="src/", help="Path to lint (default: src/)")
    
    args = parser.parse_args()
    
    # Default to all checks if no specific tool is selected
    if not any([args.ruff, args.mypy, args.security, args.unused]):
        args.all = True
    
    success = True
    
    print("🚀 Starting Schubert Toolbox Linting")
    print(f"📁 Target path: {args.path}")
    
    # Ruff linting and formatting
    if args.all or args.ruff:
        if args.fix:
            # Fix issues
            success &= run_command(
                ["ruff", "check", args.path, "--fix"],
                "Ruff linter (with fixes)"
            )
            success &= run_command(
                ["ruff", "format", args.path],
                "Ruff formatter"
            )
        else:
            # Check only
            success &= run_command(
                ["ruff", "check", args.path],
                "Ruff linter (check only)"
            )
    
    # MyPy type checking
    if args.all or args.mypy:
        success &= run_command(
            ["mypy", args.path],
            "MyPy type checking"
        )
    
    # Security checks
    if args.all or args.security:
        success &= run_command(
            ["bandit", "-r", args.path, "-f", "txt"],
            "Bandit security check"
        )
    
    # Check for unused imports specifically
    if args.unused:
        success &= run_command(
            ["ruff", "check", args.path, "--select", "F401"],
            "Unused imports check"
        )
    
    # Summary
    print(f"\n{'='*50}")
    if success:
        print("🎉 ALL CHECKS PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\nTo fix issues automatically, run:")
        print(f"  python lint.py --fix {args.path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
